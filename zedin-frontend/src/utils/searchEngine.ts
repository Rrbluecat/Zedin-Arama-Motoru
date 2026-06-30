// 🏷️ Veri Tiplerini Tanımlıyoruz (TypeScript Güvencesi)
export interface SayfaVerisi {
  url: string;
  baslik: string;
  icerik: string;
}

export interface AramaSonucu {
  sayfa: SayfaVerisi;
  skor: number;
}

export interface KagiAyarlari {
  siteSkorlari: Record<string, number>; // Domain bazlı raise/lower/block puanları
  aktifLens: 'genel' | 'forum' | 'kod' | 'akademik';
}

/**
 * 🔤 Türkçe karakterleri normalize eden ve metni arama dostu yapan fonksiyon
 */
export function zedinMetniStandardizeEt(metin: string): string {
  if (!metin) return "";
  const mapping: Record<string, string> = {
    'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
    'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
  };
  
  let sonuc = metin.toLowerCase();
  sonuc = sonuc.replace(/[çğıöşüÇĞİÖŞÜ]/g, (harf) => mapping[harf] || harf);
  // Noktalama işaretlerini temizle ve fazla boşlukları uçur
  return sonuc.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"']/g, " ").replace(/\s+/g, " ").trim();
}

/**
 * 🎯 Arama kelimelerinin başlık veya içerikte geçip geçmediğini kontrol eder
 */
export function alakaliMi(sorguKelimeleri: string[], baslik: string, icerik: string): boolean {
  const sBaslik = zedinMetniStandardizeEt(baslik);
  const sIcerik = zedinMetniStandardizeEt(icerik);
  
  // Sorgudaki kelimelerden en az birinin eşleşmesi mantığı (OR)
  return sorguKelimeleri.some(kelime => sBaslik.includes(kelime) || sIcerik.includes(kelime));
}

/**
 * 🧮 Kagi tarzı skorlama ve arama motoru lojiği
 */
export function zedinAramaMotoru(
  hamVeri: [string, string, string][], // Python API'den gelen ham array listesi
  sorgu: string,
  ayarlar: KagiAyarlari
): AramaSonucu[] {
  const standartSorgu = zedinMetniStandardizeEt(sorgu);
  const sorguKelimeleri = standartSorgu.split(" ").filter(k => k.length > 0);
  
  if (sorguKelimeleri.length === 0) return [];
  
  const sonuclar: AramaSonucu[] = [];

  for (const satir of hamVeri) {
    const [url, baslik, icerik] = satir;
    
    // 🛡️ Kagi Özelliği: Domain Engelleme (Block) kontrolü
    const domain = new URL(url).hostname.replace("www.", "");
    const kisiselSiteSkoru = ayarlar.siteSkorlari[domain] ?? 0;
    
    if (kisiselSiteSkoru <= -100) continue; // Eğer -100 veya altındaysa aramada hiç gösterme

    if (alakaliMi(sorguKelimeleri, baslik, icerik)) {
      let tabanSkor = kisiselSiteSkoru; // Kullanıcının Raise/Lower ayarı başlangıç skorudur
      
      const sBaslik = zedinMetniStandardizeEt(baslik);
      const sIcerik = zedinMetniStandardizeEt(icerik);
      
      // Detaylı kelime ağırlıklandırması
      for (const kelime of sorguKelimeleri) {
        if (sBaslik.includes(kelime)) tabanSkor += 10; // Başlıkta geçiyorsa +10 puan
        if (sIcerik.includes(kelime)) tabanSkor += 2;  // İçerikte geçiyorsa +2 puan
      }
      
      sonuclar.push({
        sayfa: { url, baslik, icerik },
        skor: tabanSkor
      });
    }
  }

  // Skorlara göre büyükten küçüğe sırala
  return sonuclar.sort((a, b) => b.skor - a.skor);
}

