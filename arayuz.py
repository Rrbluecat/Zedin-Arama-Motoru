import os
import re
import json
import glob
import threading # 🚀 Otomasyon thread yönetimi için eklendi
from flask import Flask, request, render_template_string, redirect, url_for, abort, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tarayici import link_ayıkla_ve_tarla

app = Flask(__name__)

# 🔒 [KORUMA] DDOS KORUMASI: İndeks çekme limitleri ayarlandı
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per minute"],
    storage_uri="memory://"
)

KARA_LISTE_BOTLAR = ["sqlmap", "nikto", "dirbuster", "nmap", "python-requests"]

@app.before_request
def bot_kontrolu():
    user_agent = request.headers.get('User-Agent', '').lower()
    if any(bot in user_agent for bot in KARA_LISTE_BOTLAR):
        abort(403)

# 🚀 [YENİ SHARDING SIFINIF MİMARİSİ]: RAM'deki listeyi bozmadan arka planda harflere ayıran akıllı liste nesnesi
class ShardedIndexList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shards = {}
    def append(self, item):
        super().append(item)
        self._add_to_shard(item)
    def _add_to_shard(self, item):
        if isinstance(item, list) and len(item) > 1:
            baslik = item[1]
            harf = "diger"
            if baslik:
                ilk = str(baslik)[0].lower()
                mapping = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'}
                ilk = mapping.get(ilk, ilk)
                if ilk.isalnum(): harf = ilk
            if harf not in self.shards: self.shards[harf] = []
            if item not in self.shards[harf]: self.shards[harf].append(item)

# 🚀 Sunucu başlarken tüm sharded disk dosyalarını RAM'e toplar
ARAMA_INDEKSI = ShardedIndexList()

for dosya in glob.glob("arama_indeksi_*.json"):
    try:
        with open(dosya, "r", encoding="utf-8") as f:
            for v in json.load(f):
                ARAMA_INDEKSI.append(v)
    except:
        pass

if os.path.exists("arama_indeksi.json"):
    try:
        with open("arama_indeksi.json", "r", encoding="utf-8") as f:
            for v in json.load(f):
                if v not in ARAMA_INDEKSI: ARAMA_INDEKSI.append(v)
        print(f"[*] Başarıyla {len(ARAMA_INDEKSI)} döküman belleğe yüklendi.")
    except Exception as e:
        print(f"[!] İndeks okunurken hata oluştu: {e}")

HTML_SABLON = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zedin Arama Ekosistemi</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg: #f9f9f8;
            --text: #1a1a1a;
            --muted: #6b7280;
            --accent: #5b21b6;
            --accent-light: #7c3aed;
            --border: #e5e7eb;
            --card: #ffffff;
            --hover: #f3f4f6;
            --url-color: #16a34a;
            --shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        /* 🌗 [YENİ] KOYU TEMA DEĞİŞKENLERİ - Tasarımı bozmadan renkleri override eder */
        body.dark-theme {
            --bg: #111827;
            --text: #f9fafb;
            --muted: #9ca3af;
            --accent: #a78bfa;
            --accent-light: #c084fc;
            --border: #374151;
            --card: #1f2937;
            --hover: #374151;
            --url-color: #4ade80;
            --shadow: 0 1px 3px rgba(0,0,0,0.5);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            transition: background 0.2s, color 0.2s;
        }
        /* GÖRÜNÜM KONTROLLERİ */
        .gizli { display: none !important; }

        /* [YENİ] TEMA DEĞİŞTİRME BUTONU VE NAVİGASYON */
        .top-right-nav { position: absolute; top: 20px; right: 24px; display: flex; gap: 12px; align-items: center; }
        .theme-toggle {
            background: transparent; border: 1px solid var(--border);
            color: var(--text); padding: 7px 14px; border-radius: 20px;
            cursor: pointer; font-size: 13px; font-weight: 500;
            transition: all 0.15s;
        }
        .theme-toggle:hover { background: var(--hover); border-color: var(--accent); }

        /* ANA SAYFA */
        .home-page {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .home-logo {
            font-size: 52px;
            font-weight: 800;
            color: var(--accent);
            letter-spacing: -3px;
            margin-bottom: 32px;
        }
        .home-search { width: 100%; max-width: 580px; text-align: center; }

        /* SONUÇ SAYFASI */
        .results-header {
            border-bottom: 1px solid var(--border);
            background: var(--card);
            padding: 14px 24px;
            display: flex;
            align-items: center;
            gap: 24px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow);
        }
        .results-logo {
            font-size: 22px;
            font-weight: 800;
            color: var(--accent);
            letter-spacing: -1.5px;
            text-decoration: none;
            flex-shrink: 0;
        }
        .results-body { max-width: 720px; margin: 0 auto; padding: 28px 24px; }

        /* ARAMA KUTUSU */
        .search-wrap {
            display: flex;
            align-items: center;
            background: var(--card);
            border: 1.5px solid var(--border);
            border-radius: 24px;
            padding: 8px 8px 8px 18px;
            gap: 8px;
            transition: border-color 0.15s, box-shadow 0.15s;
            box-shadow: var(--shadow);
        }
        .search-wrap:focus-within {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(91,33,182,0.12);
        }
        .search-input {
            flex: 1; border: none; background: transparent; font-size: 16px; color: var(--text); outline: none; min-width: 0;
        }
        .search-input::placeholder { color: #9ca3af; }
        .search-btn {
            background: var(--accent); color: white; border: none; padding: 9px 22px; border-radius: 18px;
            font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s; flex-shrink: 0;
        }
        .search-btn:hover { background: var(--accent-light); }

        /* KARTLAR VE METRİKLER */
        .metrics { font-size: 13px; color: var(--muted); margin: 16px 0 24px; }
        .smart-answer {
            background: var(--card); border: 1.5px solid #ddd6fe; border-left: 4px solid var(--accent);
            border-radius: 12px; padding: 18px 20px; margin-bottom: 28px; box-shadow: var(--shadow);
        }
        .smart-answer-label { font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
        .smart-answer-text { font-size: 18px; font-weight: 600; color: var(--text); }
        .result-item { padding: 18px 0; border-bottom: 1px solid var(--border); }
        .result-item:last-child { border-bottom: none; }
        .result-domain { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
        .result-favicon { width: 16px; height: 16px; border-radius: 3px; background: var(--border); }
        .result-url-text { font-size: 13px; color: var(--url-color); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 500px; }
        .result-title { font-size: 19px; font-weight: 600; margin-bottom: 5px; line-height: 1.3; }
        .result-title a { color: #1d4ed8; text-decoration: none; }
        body.dark-theme .result-title a { color: #60a5fa; }
        .result-title a:hover { text-decoration: underline; }
        .result-snippet { font-size: 14px; color: #374151; line-height: 1.6; }
        body.dark-theme .result-snippet { color: #d1d5db; }
        .no-result { text-align: center; padding: 60px 20px; color: var(--muted); }
        .no-result-icon { font-size: 40px; margin-bottom: 12px; }
        .no-result-title { font-size: 18px; font-weight: 600; color: var(--text); margin-bottom: 8px; }

        /* HİBRİT PANEL GRUPLARI */
        .admin-section { margin-top: 48px; padding-top: 24px; border-top: 1px solid var(--border); }
        .admin-label { font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px; }
        .admin-form { display: flex; gap: 8px; margin-bottom: 16px; }
        .admin-grid-form { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px; }
        .admin-input { flex: 1; border: 1.5px solid var(--border); background: var(--card); padding: 9px 14px; border-radius: 8px; font-size: 14px; color: var(--text); outline: none; transition: border-color 0.15s; }
        .admin-input:focus { border-color: var(--accent); }
        .admin-btn { background: var(--text); color: white; border: none; padding: 9px 18px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: opacity 0.15s; }
        body.dark-theme .admin-btn { background: var(--accent); }
        .admin-btn:hover { opacity: 0.8; }
        .yerel-btn { background: var(--accent); }
        @media (max-width: 600px) { .results-header { padding: 12px 16px; gap: 12px; } .results-body { padding: 20px 16px; } .result-title { font-size: 17px; } .admin-grid-form { grid-template-columns: 1fr; } }
    </style>
</head>
<body>

    <div id="ana-sayfa-ekrani" class="home-page">
        <div class="top-right-nav">
            <button onclick="temaDegistir()" class="theme-toggle" id="btn-tema-home">🌙 Koyu Tema</button>
        </div>
        <div class="home-logo">Zedin.</div>
        <div class="home-search">
            <form onsubmit="event.preventDefault(); yerelSorguGonder(this.q.value);">
                <div class="search-wrap">
                    <input type="text" name="q" class="search-input" placeholder="Ara veya !w, !yt, !g kısayollarını kullan..." autocomplete="off" autofocus>
                    <button type="submit" class="search-btn">Ara</button>
                </div>
            </form>
            <div style="margin-top: 24px; font-size: 13px; color: var(--muted); letter-spacing: 0.5px;">
                🔒 %100 Mahremiyet • Reklamsız • Takipçisiz
            </div>
        </div>
    </div>

    <div id="sonuc-ekrani" class="gizli">
        <header class="results-header">
            <a href="/" onclick="event.preventDefault(); ekranDegistir(false);" class="results-logo">Zedin.</a>
            <form onsubmit="event.preventDefault(); yerelSorguGonder(this.q.value);" style="flex:1; max-width:560px;">
                <div class="search-wrap">
                    <input type="text" name="q" id="ust-arama-input" class="search-input" autocomplete="off">
                    <button type="submit" class="search-btn">Ara</button>
                </div>
            </form>
            <button onclick="temaDegistir()" class="theme-toggle" id="btn-tema-results">🌙 Koyu Tema</button>
        </header>
        <div class="results-body">
            <div id="arama-metrikleri" class="metrics"></div>
            <div id="akilli-yanit-alani"></div>
            <div id="ana-sonuclar-alani"></div>

            <div class="admin-section">
                <div class="admin-label">Küresel Sunucu İndeksine Gönder (Railway)</div>
                <form method="POST" action="/ekle" class="admin-form">
                    <input type="text" name="yeni_url" class="admin-input" placeholder="https://ornek.com.tr">
                    <button type="submit" class="admin-btn">Sunucuda Tara</button>
                </form>

                <div class="admin-label">Kişisel Tarayıcı Hafızasına Ekle (IndexedDB)</div>
                <form onsubmit="yerelHafizayaKaydet(event);" id="yerel-ekleme-formu">
                    <div class="admin-grid-form">
                        <input type="text" id="db-url" class="admin-input" placeholder="https://yerel-site.com" required>
                        <input type="text" id="db-baslik" class="admin-input" placeholder="Site Başlığı" required>
                    </div>
                    <div class="admin-form">
                        <input type="text" id="db-icerik" class="admin-input" placeholder="Arama kelimeleri veya kısa site içeriği..." required>
                        <button type="submit" class="admin-btn yerel-btn">Tarayıcıya Göm</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
        let zedinHafizasi = [];
        let yerelVeritabanı = null;

        // 🌗 [YENİ] TEMA YÖNETİM FONKSİYONLARI
        function temaUygula(tema) {
            const btnHome = document.getElementById('btn-tema-home');
            const btnResults = document.getElementById('btn-tema-results');
            if (tema === 'dark') {
                document.body.classList.add('dark-theme');
                if(btnHome) btnHome.innerText = '☀️ Açık Tema';
                if(btnResults) btnResults.innerText = '☀️ Açık Tema';
            } else {
                document.body.classList.remove('dark-theme');
                if(btnHome) btnHome.innerText = '🌙 Koyu Tema';
                if(btnResults) btnResults.innerText = '🌙 Koyu Tema';
            }
        }

        function temaDegistir() {
            let mevcut = localStorage.getItem('zedin-tema') || 'light';
            let yeni = mevcut === 'light' ? 'dark' : 'light';
            localStorage.setItem('zedin-tema', yeni);
            temaUygula(yeni);
        }

        // 🗄️ [YENİ INTERFACE] Tarayıcı içi IndexedDB başlatıcı
        function yerelDBBaslat() {
            return new Promise((resolve, reject) => {
                const request = indexedDB.open("ZedinYerelHafiza", 1);

                request.onupgradeneeded = (e) => {
                    const db = e.target.result;
                    if (!db.objectStoreNames.contains("siteler")) {
                        // Esnek şema: Düz dizi [url, baslik, icerik] yapısıyla tam uyumlu depolama
                        db.createObjectStore("siteler", { autoIncrement: true });
                    }
                };

                request.onsuccess = (e) => {
                    yerelVeritabanı = e.target.result;
                    resolve(yerelVeritabanı);
                };

                request.onerror = (e) => reject(e.target.error);
            });
        }

        // 📥 Tarayıcı hafızasındaki tüm kişisel dökümanları çeken fonksiyon
        function yerelVerileriGetir() {
            return new Promise((resolve) => {
                if (!yerelVeritabanı) return resolve([]);

                const transaction = yerelVeritabanı.transaction("siteler", "readonly");
                const store = transaction.objectStore("siteler");
                const istek = store.getAll();

                istek.onsuccess = () => resolve(istek.result || []);
                istek.onerror = () => resolve([]);
            });
        }

        // 💾 Kullanıcının gizli/yerel döküman eklemesini sağlayan fonksiyon
        async function yerelHafizayaKaydet(e) {
            e.preventDefault();
            const url = document.getElementById("db-url").value.strip ? document.getElementById("db-url").value.strip() : document.getElementById("db-url").value.trim();
            const baslik = document.getElementById("db-baslik").value.trim();
            const icerik = document.getElementById("db-icerik").value.trim();

            if (!url || !baslik || !icerik) return;

            if (!yerelVeritabanı) {
                alert("Hata: Tarayıcı veritabanı hazır değil.");
                return;
            }

            const transaction = yerelVeritabanı.transaction("siteler", "readwrite");
            const store = transaction.objectStore("siteler");

            // Yapıyı bozmamak adına indeks_olusturucu dizilimi ile tam uyumlu array formatı: [url, baslik, icerik]
            store.add([url, baslik, icerik]);

            transaction.oncomplete = () => {
                alert("🎉 Site sadece senin tarayıcına (IndexedDB) başarıyla kazındı!");
                document.getElementById("yerel-ekleme-formu").reset();
                // Mevcut aramayı anında güncellemek için tetikle
                const mevcutSorgu = document.getElementById('ust-arama-input').value;
                if (mevcutSorgu) yerelSorguGonder(mevcutSorgu);
            };
        }

        // Sayfa açılır açılmaz sunucuyu yormadan sıkıştırılmış indeksi arka planda indiriyoruz
        async function indeksiIndir() {
            // 🌗 Kayıtlı temayı yükle
            temaUygula(localStorage.getItem('zedin-tema') || 'light');

            try {
                // Önce tarayıcı lokal veritabanını hazır hale getiriyoruz
                await yerelDBBaslat();
            } catch (err) {
                console.error("IndexedDB başlatılamadı, sadece küresel mod aktif:", err);
            }

            try {
                const response = await fetch('/api/indeks');
                if (response.status === 429) {
                    console.warn("DDoS koruması tetiklendi. İstekler sınırlandırıldı.");
                    return;
                }
                zedinHafizasi = await response.json();

                // Eğer URL'de önceden arama parametresi varsa direkt aramayı çalıştır
                const urlParams = new URLSearchParams(window.location.search);
                const q = urlParams.get('q');
                if (q) {
                    yerelSorguGonder(q);
                }
            } catch (err) {
                console.error("İndeks yükleme hatası:", err);
            }
        }

        function ekranDegistir(sonucModu) {
            const anaSayfa = document.getElementById('ana-sayfa-ekrani');
            const sonucSayfasi = document.getElementById('sonuc-ekrani');
            if (sonucModu) {
                anaSayfa.classList.add('gizli');
                sonucSayfasi.classList.remove('gizli');
            } else {
                sonucSayfasi.classList.add('gizli');
                anaSayfa.classList.remove('gizli');
                window.history.pushState({}, '', '/');
            }
        }

        function snippetKontrol(sorgu) {
            // Matematiksel işlem kontrolü (RegEx)
            if (/^[0-9\\s\\+\\-\\*\\/\\(\\)\\.]+$/.test(sorgu)) {
                try {
                    return `${sorgu} = ${eval(sorgu)}`;
                } catch { return null; }
            }
            // Selamlama bot tetikleyicisi
            const low = sorgu.toLowerCase();
            if (["sa", "selam", "merhaba"].includes(low)) {
                return "Merhaba! Zedin Arama Motoruna hoş geldiniz.";
            }
            return null;
        }

        function alakaliMi(sorguKelimeleri, baslik, icerik) {
            const birlesikMetin = (baslik + " " + icerik).toLowerCase();
            for (let kelime of sorguKelimeleri) {
                if (kelime.length > 2 && !birlesikMetin.includes(kelime)) {
                    return false;
                }
            }
            return true;
        }

        // 🧠 [HİBRİT MOTOR] Artık hem sunucu belleğini hem IndexedDB verilerini asenkron tarıyor
        async function yerelSorguGonder(sorgu) {
            sorgu = sorgu.trim();
            if (!sorgu) return;

            // 🎯 [YENİ] KAGI TARZI HIZLI KISAYOLLAR (Bang Kısayolları)
            // Kullanıcıyı doğrudan ilgili dış kaynağa yönlendirir ve aramayı durdurur.
            if (sorgu.startsWith('!w ')) {
                window.location.href = 'https://tr.wikipedia.org/wiki/Special:Search?search=' + encodeURIComponent(sorgu.substring(3));
                return;
            }
            if (sorgu.startsWith('!yt ')) {
                window.location.href = 'https://www.youtube.com/results?search_query=' + encodeURIComponent(sorgu.substring(4));
                return;
            }
            if (sorgu.startsWith('!g ')) {
                window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(sorgu.substring(3));
                return;
            }

            // URL'i güncelle (Paylaşılabilir arama linkleri için)
            window.history.pushState({}, '', '?q=' + encodeURIComponent(sorgu));
            document.getElementById('ust-arama-input').value = sorgu;
            ekranDegistir(true);

            // 🎯 [YENİ SHARDING AKILLI DİNAMİK YÜKLEYİCİ]: Sadece aranan kelimenin baş harfine ait JSON parçasını indirir, RAM uçuşa geçer!
            try {
                let harf = "diger";
                if (sorgu.length > 0) {
                    let ilk = sorgu.charAt(0).toLowerCase();
                    const mapping = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'};
                    ilk = mapping[ilk] || ilk;
                    if (/^[a-z0-9]$/.test(ilk)) { harf = ilk; }
                }
                const shardRes = await fetch('/api/indeks?harf=' + harf);
                if (shardRes.ok) {
                    const shardVerisi = await shardRes.json();
                    shardVerisi.forEach(item => {
                        if (!zedinHafizasi.some(x => x[0] === item[0])) { zedinHafizasi.push(item); }
                    });
                }
            } catch(err) { console.error("Shard yükleme hatası:", err); }

            const t0 = performance.now();
            let sonuclar = [];

            // 1. Akıllı Yanıt (Snippet) Denetimi
            const hızlıYanit = snippetKontrol(sorgu);
            const akilliAlan = document.getElementById('akilli-yanit-alani');
            if (hızlıYanit) {
                akilliAlan.innerHTML = `
                    <div class="smart-answer">
                        <div class="smart-answer-label">Hızlı Yanıt</div>
                        <div class="smart-answer-text">${hızlıYanit}</div>
                    </div>`;
            } else {
                akilliAlan.innerHTML = '';
            }

            // 2. [HİBRİT BİRLEŞTİRME] Tarayıcı içi IndexedDB verilerini çek ve sunucu havuzuna bağla
            const yerelKisiselSiteler = await yerelVerileriGetir();
            const tamAramaHavuzu = [...zedinHafizasi, ...yerelKisiselSiteler];

            // 3. İndeks Üzerinde Filtreleme ve Arama
            const sorguKelimeleri = sorgu.split(/\\s+/).map(k => k.toLowerCase()).filter(k => k.length > 1);

            if (sorguKelimeleri.length > 0 && !hızlıYanit) {
                for (let sayfa of tamAramaHavuzu) {
                    const url = sayfa[0] || "";
                    const baslik = sayfa[1] || "";
                    const icerik = sayfa[2] || "";

                    if (alakaliMi(sorguKelimeleri, baslik, icerik)) {
                        // Basit BM25/Alakalılık puanlaması simülasyonu
                        let skor = 0;
                        for (let kelime of sorguKelimeleri) {
                            if (baslik.toLowerCase().includes(kelime)) skor += 10;
                            if (icerik.toLowerCase().includes(kelime)) skor += 2;
                        }
                        sonuclar.push({ sayfa, skor });
                    }
                }
                // Puanı yüksek olanı en üste sırala
                sonuclar.sort((a, b) => b.skor - a.skor);
            }

            const t1 = performance.now();
            const aramaSuresi = ((t1 - t0) / 1000).toFixed(3);

            // Metrikleri ve Sonuç Listesini DOM'a Yazdır
            document.getElementById('arama-metrikleri').innerHTML = `${sonuclar.length} sonuç &mdash; ${aramaSuresi} saniye`;

            const sonuclarAlani = document.getElementById('ana-sonuclar-alani');
            sonuclarAlani.innerHTML = '';

            const hamSonuclar = sonuclar.map(s => s.sayfa).slice(0, 20); // İlk 20 sonucu göster

            if (hamSonuclar.length > 0) {
                hamSonuclar.forEach(satir => {
                    const div = document.createElement('div');
                    div.className = 'result-item';
                    div.innerHTML = `
                        <div class="result-domain">
                            <img class="result-favicon" src="https://www.google.com/s2/favicons?domain=${satir[0]}&sz=16" onerror="this.style.display='none'">
                            <span class="result-url-text">${satir[0]}</span>
                        </div>
                        <h3 class="result-title">
                            <a href="${satir[0]}" target="_blank" rel="noopener">${satir[1]}</a>
                        </h3>
                        <p class="result-snippet">${satir[2]}...</p>
                    `;
                    sonuclarAlani.appendChild(div);
                });
            } else if (!hızlıYanit) {
                sonuclarAlani.innerHTML = `
                    <div class="no-result">
                        <div class="no-result-icon">🔍</div>
                        <div class="no-result-title">Sonuç bulunamadı</div>
                        <p>${sorgu} için herhangi bir sonuç bulunamadı.</p>
                    </div>`;
            }
        }

        window.onload = indeksiIndir;
    </script>
</body>
</html>
"""

@app.route("/")
def ara():
    return render_template_string(HTML_SABLON)

# 🚀 [YENİ ULTRA SHARD API]: İstek harf içeriyorsa sadece o harfe ait hafifletilmiş paketi fırlatır!
@app.route("/api/indeks")
def api_indeks():
    harf = request.args.get("harf", "").lower()
    if harf and hasattr(ARAMA_INDEKSI, 'shards'):
        return jsonify(ARAMA_INDEKSI.shards.get(harf, []))
    return jsonify(ARAMA_INDEKSI)

@app.route("/ekle", methods=["POST"])
@limiter.limit("3 per minute")
def ekle():
    hedef_url = request.form.get("yeni_url", "").strip()
    if hedef_url:
        link_ayıkla_ve_tarla(hedef_url, max_sayfa=50)
    return redirect(url_for("ara"))

# 🚀 [YENİ GİZLİ OTOMASYON ROTASI]: Sunucu açıkken arka planda tohum listesini taratır
@app.route("/zedin-sihirbazini-uyandir-99")
def otomatik_besle_tetikle():
    from tarayici import zedin_otomatik_besleme
    # Asenkron Thread sayesinde sunucu donmaz, arama motoru aktif kalır
    thread = threading.Thread(target=zedin_otomatik_besleme)
    thread.start()
    return "Zedin örümcekleri canlı sunucu açıkken arka planda çalışmaya başladı! Veriler anlık işleniyor."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

