/**
 * 🧠 ZEDIN AKIL MOTORU (zedin_akil.js) - Mobil Debug ve Güvenli Mod Entegreli
 * Yapay Zeka, Lens Filtreleri, Site Puanlama ve Kullanıcı Scriptleri Yönetim Merkezi
 */

// 1. 🎛️ LOKAL YAPILANDIRMA VE VERİ DEPOLAMA (LocalStorage tabanlı)
const ZedinAkılAyarları = {
    // Engellenen ve öncelikli siteler (Site Özelleştirme / Ranking)
    siteSkorları: JSON.parse(localStorage.getItem('zedin-site-skorlari')) || {
        'pinterest.com': -100,      // Çöp siteleri tamamen aşağı it veya engelle
        'stackoverflow.com': 50,    // Güvenilir siteleri en üste fırlat
        'github.com': 40
    },
    // Aktif lens (Varsayılan: genel arama)
    aktifLens: localStorage.getItem('zedin-aktif-lens') || 'genel',
    
    // Model yükleme durumu ve debug takibi
    modelYuklendimi: false,
    sonHataMesaji: null // Telefonda F12 olmadan hatayı yakalamak için yeni alan
};

// 2. 🦥 LOKAL YAPILANDIRILMIŞ YAPAY ZEKA (Açık Kaynak Özetleme Motoru)
let zedinYZEngine = null;

async function zedinAI_Baslat() {
    console.log("[*] Zedin Akıl Örüntüsü Uyanıyor... Model yükleniyor.");
    try {
        // Dinamik olarak Transformers.js kütüphanesini ve ENV (ortam ayarlarını) CDN üzerinden çağırıyoruz
        const { pipeline, env } = await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.14.0');
        
        // 🛠️ MOBİL GÜVENLİK VE "UNAUTHORIZED ACCESS" HATASI ÇÖZÜMÜ:
        env.allowLocalModels = false; // Localde model aramayı kapat, doğrudan sunucudan çek
        env.useBrowserCache = false;  // Tarayıcının katı güvenlik duvarına (Cache Sandbox) takılmamak için önbelleği kapat
        
        // Özetleme (summarization) görevleri için modeli hafızaya alıyoruz
        zedinYZEngine = await pipeline('summarization', 'Xenova/LaMini-Flan-T5-78M');
        ZedinAkılAyarları.modelYuklendimi = true;
        console.log("[+] Zedin Yapay Zeka Motoru Hazır ve Lokalinde Çalışıyor!");
    } catch (err) {
        console.error("[-] Yapay zeka modeli yüklenirken hata oluştu:", err);
        // Hatayı hafızaya alıyoruz ki telefonda ekrana basabilelim
        ZedinAkılAyarları.sonHataMesaji = err.message || String(err);
    }
}

// 3. 📝 SCRIPT TABANLI YAPAY ZEKA EĞİTİMİ (Context & Prompt Engineering)
async function zedinAI_HizliYanitUret(sorgu, aramaSonuclari) {
    if (!ZedinAkılAyarları.modelYuklendimi || !zedinYZEngine) {
        return "Yapay zeka modeli şu an devre dışı, ancak arama sonuçları ve lens filtreleri aktif!";
    }

    // [SCRIPT ENJEKSİYONU] Arama sonuçlarından ilk 3 tanesinin özetini alıp bağlam oluşturuyoruz
    let baglamMetni = aramaSonuclari.slice(0, 3).map(s => s.sayfa[2]).join(" ");
    
    // Modelimizi script vasıtasıyla yönlendirdiğimiz kısım:
    const sistemTalimati = `Soru: ${sorgu}. Verilen bilgilere göre net ve kısa bir Türkçe cevap üret. Bilgi: ${baglamMetni}`;

    try {
        const out = await zedinYZEngine(sistemTalimati, {
            max_new_tokens: 60,
            temperature: 0.3 // Daha tutarlı ve uydurmayan cevaplar için düşük tutuyoruz
        });
        return out[0].summary_text || "Yanıt oluşturulamadı.";
    } catch (e) {
        return "Lokal özetleme motoru bir hata ile karşılaştı.";
    }
}

// 4. 👓 LENS (FİLTRELEME) SİSTEMİ
const ZedinLensler = {
    'genel': (sonuc) => true,
    'forum': (sonuc) => {
        const url = sonuc[0].toLowerCase();
        return url.includes('reddit.com') || url.includes('eksisozluk.com') || url.includes('donanimhaber.com');
    },
    'kod': (sonuc) => {
        const url = sonuc[0].toLowerCase();
        return url.includes('github.com') || url.includes('stackoverflow.com') || url.includes('medium.com/engineering');
    },
    'akademik': (sonuc) => {
        const url = sonuc[0].toLowerCase();
        return url.includes('.edu') || url.includes('scholar') || url.includes('wikipedia.org');
    }
};

// 5. 🎯 SITE PUANLAMA VE SIRALAMA MOTORU (Ranking)
function zedinSkorlaVeFiltrele(hamHavuz) {
    let filtrelenmişHavuz = [];
    const aktifLensFonksiyonu = ZedinLensler[ZedinAkılAyarları.aktifLens] || ZedinLensler['genel'];

    for (let sayfa of hamHavuz) {
        // Önce aktif lens filtresinden geçiyor mu bakıyoruz
        if (!aktifLensFonksiyonu(sayfa)) continue;

        let url = sayfa[0] || "";
        let tabanSkor = 0;

        // Kullanıcının kişisel site puanlamasını işin içine katıyoruz
        Object.keys(ZedinAkılAyarları.siteSkorları).forEach(domain => {
            if (url.includes(domain)) {
                tabanSkor += ZedinAkılAyarları.siteSkorları[domain];
            }
        });

        // Eğer site tamamen engellenmişse (-100 veya altı) havuzdan tamamen eliyoruz
        if (tabanSkor <= -100) continue;

        filtrelenmişHavuz.push({ sayfa, kisiselSkor: tabanSkor });
    }

    return filtrelenmişHavuz;
}

// Sayfa yüklendiğinde yapay zekayı asenkron olarak ayağa kaldır ve telefonda test için gösterge ekle
document.addEventListener("DOMContentLoaded", () => {
    // Ekranın en üstüne yapışık küçük bir durum çubuğu oluşturuyoruz (F12 alternatifi)
    const aiStatus = document.createElement('div');
    aiStatus.id = "ai-status-bar";
    aiStatus.style = "position:fixed; top:0; left:0; width:100%; background:#f59e0b; color:white; text-align:center; font-size:12px; padding:8px; z-index:9999; font-family:sans-serif; font-weight:bold; box-shadow:0 2px 5px rgba(0,0,0,0.2); transition: all 0.3s ease;";
    aiStatus.innerText = "🧠 Zedin AI: Model yükleniyor (Lensler ve Puanlama Aktif)...";
    document.body.appendChild(aiStatus);

    // Başlatma fonksiyonunu çağırıp bittiğinde göstergeyi güncelliyoruz
    zedinAI_Baslat().then(() => {
        if (ZedinAkılAyarları.modelYuklendimi) {
            aiStatus.style.background = "#16a34a"; // Model yüklenince yeşil yap
            aiStatus.innerText = "🧠 Zedin AI: Lokal Model Hazır! Test edebilirsin.";
            
            // 4 saniye sonra ekrandan otomatik kaybolur
            setTimeout(() => aiStatus.remove(), 4000);
        } else {
            // Hata durumunda kırmızı yap ve alt satıra gerçek hata kodunu yaz (DEBUG)
            aiStatus.style.background = "#dc2626"; 
            aiStatus.style.padding = "12px 8px";
            
            const hataDetayi = ZedinAkılAyarları.sonHataMesaji || "Bilinmeyen tarayıcı kısıtlaması (CORS veya Hızlı Kapatma).";
            aiStatus.innerHTML = `⚠️ Zedin AI Modeli Yüklenemedi!<br><span style="font-weight:normal; font-size:10px; opacity:0.9; display:block; margin-top:4px; word-break:break-all;">Hata: ${hataDetayi}</span><br><span style="font-size:11px; color:#fef08a;">[Lens filtreleri ve Sıralama şu an sorunsuz çalışıyor, test edebilirsin!]</span>`;
            
            // Kullanıcı hatayı rahatça okuyabilsin diye hata çubuğunu ekranda daha uzun (10 saniye) tutuyoruz
            setTimeout(() => aiStatus.remove(), 10000);
        }
    }).catch(err => {
        // Genel çökme koruması
        aiStatus.style.background = "#dc2626";
        aiStatus.innerText = "❌ Kritik Motor Hatası! Lensler açık tutuluyor.";
        setTimeout(() => aiStatus.remove(), 5000);
    });
});

