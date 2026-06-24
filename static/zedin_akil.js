/**
 * 🧠 ZEDIN AKIL MOTORU (zedin_akil.js) - Sunucusuz & Kararlı Proxy API Modu
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

// 2. 🦥 BULUT TABANLI YAPAY ZEKA (CORS Engeline Takılmayan Alternatif Genel API)
// Tarayıcı kısıtlamalarını aşmak için açık kaynaklı ve anonim istek kabul eden metin API'sini kullanıyoruz
const FREE_AI_API_URL = "https://text.pollinations.ai/";

async function zedinAI_Baslat() {
    console.log("[*] Zedin Akıl Örüntüsü Genel API Modunda Başlatılıyor...");
    try {
        // Sunucunun ayakta olup olmadığını test etmek için hafif bir istek atıyoruz
        const response = await fetch(`${FREE_AI_API_URL}ping`);
        
        if (response.ok) {
            ZedinAkılAyarları.modelYuklendimi = true;
            console.log("[+] Zedin Yapay Zeka Bulut Motoru Bağlantısı Başarılı!");
            return true;
        } else {
            throw new Error(`CORS veya Sunucu Reddi (Durum: ${response.status})`);
        }
    } catch (err) {
        console.error("[-] Yapay zeka API bağlantı hatası:", err);
        ZedinAkılAyarları.sonHataMesaji = "Tarayıcı isteği engelledi (CORS / Güvenlik Duvarı).";
        ZedinAkılAyarları.modelYuklendimi = false;
        return false;
    }
}

// 3. 📝 SCRIPT TABANLI YAPAY ZEKA EĞİTİMİ (Context & Prompt Engineering)
async function zedinAI_HizliYanitUret(sorgu, aramaSonuclari) {
    // API kapalı olsa bile kullanıcıya uyarı verip filtreleri açık tutuyoruz
    if (!ZedinAkılAyarları.modelYuklendimi) {
        return "Yapay zeka motoru şu an bypass modunda, arama sonuçları ve lens filtreleri aktif!";
    }

    // Arama sonuçlarından ilk 3 tanesinin özetini alıp bağlam oluşturuyoruz
    let baglamMetni = aramaSonuclari.slice(0, 3).map(s => s.sayfa[2]).join(" ");
    
    // Modelin net cevap vermesi için promptu URL'e uygun hale getiriyoruz
    const sistemTalimati = `Soru: ${sorgu}. Verilen bilgilere göre net ve kısa bir Türkçe cevap üret. Bilgi: ${baglamMetni}`;
    const encodePrompt = encodeURIComponent(sistemTalimati);

    try {
        // Pollinations AI, GET isteği ile doğrudan metin döndürdüğü için tarayıcı engeline takılmaz
        const response = await fetch(`${FREE_AI_API_URL}${encodePrompt}?model=openai&json=false`);

        if (!response.ok) throw new Error("Yanıt alınamadı");
        
        const resultText = await response.text();
        return resultText || "Yanıt oluşturulamadı.";
    } catch (e) {
        return "Yapay zeka motorundan cevap alınırken bir kısıtlama oluştu.";
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
    aiStatus.innerText = "🧠 Zedin AI: Güvenli API bağlantısı kuruluyor...";
    document.body.appendChild(aiStatus);

    zedinAI_Baslat().then(() => {
        if (ZedinAkılAyarları.modelYuklendimi) {
            aiStatus.style.background = "#16a34a"; 
            aiStatus.innerText = "🧠 Zedin AI: Güvenli Bulut Motoru Hazır!";
            setTimeout(() => aiStatus.remove(), 4000);
        } else {
            aiStatus.style.background = "#dc2626"; 
            aiStatus.style.padding = "12px 8px";
            
            const hataDetayi = ZedinAkılAyarları.sonHataMesaji || "Tarayıcı CORS kısıtlaması.";
            aiStatus.innerHTML = `⚠️ Zedin AI Modeli Aktif Edilemedi!<br><span style="font-weight:normal; font-size:10px; opacity:0.9; display:block; margin-top:4px; word-break:break-all;">Hata: ${hataDetayi}</span><br><span style="font-size:11px; color:#fef08a;">[Lens filtreleri ve Sıralama şu an sorunsuz çalışıyor, test edebilirsin!]</span>`;
            
            setTimeout(() => aiStatus.remove(), 10000);
        }
    }).catch(err => {
        aiStatus.style.background = "#dc2626";
        aiStatus.innerText = "❌ Kritik Motor Hatası! Lensler açık tutuluyor.";
        setTimeout(() => aiStatus.remove(), 5000);
    });
});

