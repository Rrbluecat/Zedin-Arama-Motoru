import os
import math
from datetime import datetime

HEDEF_DOSYA = "domainler.txt"

# KÜRESEL ÇÖP VE DEV SİTELERİN FİLTRESİ
KARA_LISTE_KELIMELER = [
    "adclick", "doubleclick", "adsense", "analytics", "tracker",
    "affiliate", "casino", "bet", "kumar", "porn", "adult",
    "betting", "slot", "popup", "banner", "facebook", "instagram", 
    "twitter", "amazon", "netflix", "apple", "microsoft", "google"
]

# .com UZANTILI SİTELER İÇİN TÜRKÇE DOĞRULAMA ANAHTARLARI
TURKCE_ANAHTARLAR = [
    "haber", "sozcu", "milliyet", "hurriyet", "turk", "turkiye", 
    "indir", "film", "izle", "oyun", "bilgi", "kitap", "ders", 
    "okul", "universite", "forum", "blog", "gazete", "pazar", "magaza",
    "yazilim", "teknoloji", "satis", "urun", "hizmet", "sozluk"
]

def shannon_entropi(metin):
    if not metin: return 0
    frekanslar = {}
    for karakter in metin:
        frekanslar[karakter] = frekanslar.get(karakter, 0) + 1
    entropi = 0
    toplam_karakter = len(metin)
    for sayi in frekanslar.values():
        olasilik = sayi / toplam_karakter
        entropi -= olasilik * math.log2(olasilik)
    return entropi

def domain_to_vector(ana_isim):
    alfabe = "abcdefghijklmnopqrstuvwxyz0123456789-"
    vektor = [0] * len(alfabe)
    for karakter in ana_isim:
        if karakter in alfabe:
            vektor[alfabe.index(karakter)] += 1
    toplam = sum(vektor)
    if toplam > 0:
        vektor = [v / toplam for v in vektor]
    return vektor

def kosinus_benzerligi(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0: return 0
    return dot_product / (norm_a * norm_b)

def gelismis_tavizsiz_suzgec(domain, ai_referanslar):
    saf = domain.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0].lower()
    if not saf or "." not in saf: 
        return False
        
    # =========================================================================
    # 1. MUTLAK KORUMA: Sadece .com veya .tr ile biten sitelere izin ver!
    # (.pro, .xyz, .net, .org, .cc, .co, .online vb. anında kalıcı olarak elenir)
    # =========================================================================
    if not (saf.endswith(".com") or saf.endswith(".tr")):
        return False

    parcalar = saf.split('.')
    ana_isim = parcalar[0]
    
    # 2. KORUMA: Kelime uzunluğu ve küresel çöp karalistesi
    if len(ana_isim) < 3 or len(ana_isim) > 40: return False
    if any(k in ana_isim for k in KARA_LISTE_KELIMELER): return False
    if any(r in ana_isim for r in ["asdasd", "qweqwe", "zxcv", "dfgh"]): return False

    # 3. KORUMA: Dil ve Sektör Odaklılık Filtresi
    if saf.endswith(".tr"):
        # Resmi .tr veya .com.tr uzantılı ise Türkiye tescillidir, kabul edilir.
        pass
    else:
        # Uzantı .com ise, yabancı siteleri ayıklamak için İÇİNDE MUTLAKA Türkçe anahtar kelime geçmeli
        if not any(k in ana_isim for k in TURKCE_ANAHTARLAR):
            return False

    # 4. KORUMA: Karakter ve Frekans Dengesi (Rastgele klavye vuruşları)
    sesli = set("aeıioöuü")
    harfler = [c for c in ana_isim if c.isalpha()]
    if harfler:
        s_orani = sum(1 for c in harfler if c in sesli) / len(harfler)
        if len(ana_isim) > 6 and (s_orani < 0.12 or s_orani > 0.85): return False

    sessiz_blok = max((len(g) for g in "".join(c if c not in "aeıioöuü" and c.isalpha() else " " for c in ana_isim).split()), default=0)
    sayi_blok = max((len(g) for g in "".join(c if c.isdigit() else " " for c in ana_isim).split()), default=0)
    if sessiz_blok > 4 or sayi_blok > 4: return False

    # 5. KORUMA: Entropi (Kaos Kontrolü)
    if len(ana_isim) > 8 and shannon_entropi(ana_isim) > 3.4: return False

    # 6. KORUMA: Ağırlaştırılmış Yapay Zeka Semantik Vektör Analizi
    v = domain_to_vector(ana_isim)
    en_yuksek_benzerlik = max(kosinus_benzerligi(v, ref) for ref in ai_referanslar)
    
    # .tr dışındaki genel .com uzantıları için AI sınırını yüksek tutuyoruz
    limit = 0.12 if saf.endswith(".tr") else 0.28
    if en_yuksek_benzerlik < limit: 
        return False

    return True

def demir_perde_calistir():
    if not os.path.exists(HEDEF_DOSYA):
        print(f"[!] {HEDEF_DOSYA} bulunamadı!")
        return

    print("=" * 60)
    print(" 🛡️  ZEDIN MUTLAK BEYAZ LİSTE FİLTRE MOTORU BAŞLATILDI 🛡️")
    print("=" * 60)
    print("[*] Sadece .com ve .tr içeren kaliteli siteler seçiliyor...\n")

    ai_referanslar = [
        domain_to_vector("teknoloji"), domain_to_vector("haberler"),
        domain_to_vector("universite"), domain_to_vector("bilgi-deposu")
    ]

    GECICI_DOSYA = "domainler_temp.txt"
    okunan_satir = 0
    temiz_sayisi = 0
    baslangic_zamani = datetime.now()

    with open(HEDEF_DOSYA, "r", encoding="utf-8", errors="ignore") as kaynak, \
         open(GECICI_DOSYA, "w", encoding="utf-8") as hedef:
         
        for satir in kaynak:
            okunan_satir += 1
            satir_veri = satir.strip()
            if not satir_veri: continue
            
            # Sıra numarası temizliği
            domain = satir_veri.split(',')[1] if "," in satir_veri else satir_veri

            if gelismis_tavizsiz_suzgec(domain, ai_referanslar):
                hedef.write(f"{domain}\n")
                temiz_sayisi += 1

            if okunan_satir % 100000 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Analiz Durumu: {okunan_satir} satır tarandı...")

    if os.path.exists(GECICI_DOSYA):
        os.replace(GECICI_DOSYA, HEDEF_DOSYA)

    gecen_sure = datetime.now() - baslangic_zamani
    print("\n" + "=" * 60)
    print("[+] FİLTRELEME İŞLEMİ TAMAMLANDI!")
    print(f"    İncelenen Toplam Satır      : {okunan_satir}")
    print(f"    Kalan Kusursuz Havuz (.com/.tr): {temiz_sayisi}")
    print(f"    Silinen Çöp / Diğer Uzantı  : {okunan_satir - temiz_sayisi}")
    print(f"    Harcanan Toplam Süre        : {gecen_sure.seconds} saniye")
    print(f"    '{HEDEF_DOSYA}' dosyası tertemiz olarak güncellendi.")
    print("=" * 60)

if __name__ == "__main__":
    demir_perde_calistir()

