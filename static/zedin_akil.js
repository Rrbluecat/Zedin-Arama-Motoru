/**
 * 🧠 ZEDIN AKIL MOTORU (zedin_akil.js) - Kesin Çözüm / Kararlı Model
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
    sonHataMesaji: null 
};

// 2. 🦥 LOKAL YAPILANDIRILMIŞ YAPAY ZEKA (Açık Kaynak Özetleme Motoru)
let zedinYZEngine = null;

async function zedinAI_Baslat() {
    console.log("[*] Zedin Akıl Örüntüsü Uyanıyor... Model yükleniyor.");
    try {
        // Dinamik olarak Transformers.js kütüphanesini ve ENV (ortam ayarlarını) CDN üzerinden çağırıyoruz
        const { pipeline, env } = await import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.14.0');
        
        // Mobil uyumluluk ve önbellek stabilizasyonu
        env.allowLocalModels = false; 
        env.useBrowserCache = true;   
        
        // 🛠️ ALTERNATİF VE KARARLI MODEL:
        // transformers.js ile dosya yapısı tam uyumlu olan distilbart modeline geçiş yaptık.
        zedinYZEngine = await pipeline('summarization', 'Xenova/distilbart-cnn-6-6');
        
        ZedinAkılAyarları.modelYuklendimi = true;
        console.log("[+] Zedin Yapay Zeka Motoru Hazır ve Lokalinde Çalışıyor!");
    } catch (err) {
        console.error("[-] Yapay zeka modeli yüklenirken hata oluştu:", err);
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
            temperature: 0.3 
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
        if (!aktifLensFonksiyonu(sayfa)) continue;

        let url = sayfa[0] || "";
        let tabanSkor = 0;

        Object.keys(ZedinAkılAyarları.siteSkorları).forEach(domain => {
            if (url.includes(domain)) {
                tabanSkor += ZedinAkılAyarları.siteSkorları[domain];
            }
        });

        if (tabanSkor <= -100) continue;

        filtrelenmişHavuz.push({ sayfa, kisiselSkor: tabanSkor });
    }

    return filtrelenmişHavuz;
}

// Sayfa yüklendiğinde işlemleri başlat
document.addEventListener("DOMContentLoaded", () => {
    const aiStatus = document.createElement('div');
    aiStatus.id = "ai-status-bar";
    aiStatus.style = "position:fixed; top:0; left:0; width:100%; background:#f59e0b; color:white; text-align:center; font-size:12px; padding:8px; z-index:9999; font-family:sans-serif; font-weight:bold; box-shadow:0 2px 5px rgba(0,0,0,0.2); transition: all 0.3s ease;";
    aiStatus.innerText = "🧠 Zedin AI: Model arka planda yükleniyor (Lensler ve Puanlama Aktif)...";
    document.body.appendChild(aiStatus);

    zedinAI_Baslat().then(() => {
        if (ZedinAkılAyarları.modelYuklendimi) {
            aiStatus.style.background = "#16a34a"; 
            aiStatus.innerText = "🧠 Zedin AI: Lokal Model Hazır! Test edebilirsin.";
            setTimeout(() => aiStatus.remove(), 4000);
        } else {
            aiStatus.style.background = "#dc2626"; 
            aiStatus.style.padding = "12px 8px";
            
            const hataDetayi = ZedinAkılAyarları.sonHataMesaji || "Bağlantı veya yükleme hatası.";
            aiStatus.innerHTML = `⚠️ Zedin AI Modeli Yüklenemedi!<br><span style="font-weight:normal; font-size:10px; opacity:0.9; display:block; margin-top:4px; word-break:break-all;">Hata: ${hataDetayi}</span><br><span style="font-size:11px; color:#fef08a;">[Lens filtreleri ve Sıralama şu an sorunsuz çalışıyor, test edebilirsin!]</span>`;
            
            setTimeout(() => aiStatus.remove(), 10000);
        }
    }).catch(err => {
        aiStatus.style.background = "#dc2626";
        aiStatus.innerText = "❌ Kritik Motor Hatası! Lensler açık tutuluyor.";
        setTimeout(() => aiStatus.remove(), 5000);
    });
});

