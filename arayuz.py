import os
import re
import sqlite3
import time
from flask import Flask, request, render_template_string, redirect, url_for, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tarayici import link_ayıkla_ve_tarla

app = Flask(__name__)

# 🔒 [YENİ] DDOS KORUMASI: Sunucu kaynaklarını korumak için istek sınırlandırıcı
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["40 per minute"], # Genel olarak dakikada en fazla 40 istek hakkı
    storage_uri="memory://"           # Ekstra RAM tüketmemesi için bellekte çalışır
)

# 🔒 [YENİ] ZARARLI BOT FİLTRESİ: Sunucuyu taramaya çalışan bilinen araçları engeller
KARA_LISTE_BOTLAR = ["sqlmap", "nikto", "dirbuster", "nmap", "python-requests"]

@app.before_request
def bot_kontrolu():
    user_agent = request.headers.get('User-Agent', '').lower()
    if any(bot in user_agent for bot in KARA_LISTE_BOTLAR):
        abort(403) # Zararlı botların erişimini doğrudan engelle

HTML_SABLON = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if sorgu %}{{ sorgu }} - Zedin{% else %}Zedin Arama{% endif %}</title>
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
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
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
        .home-search {
            width: 100%;
            max-width: 580px;
        }
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
        .results-body {
            max-width: 720px;
            margin: 0 auto;
            padding: 28px 24px;
        }
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
            flex: 1;
            border: none;
            background: transparent;
            font-size: 16px;
            color: var(--text);
            outline: none;
            min-width: 0;
        }
        .search-input::placeholder { color: #9ca3af; }
        .search-btn {
            background: var(--accent);
            color: white;
            border: none;
            padding: 9px 22px;
            border-radius: 18px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
            flex-shrink: 0;
        }
        .search-btn:hover { background: var(--accent-light); }
        /* METRİK */
        .metrics {
            font-size: 13px;
            color: var(--muted);
            margin: 16px 0 24px;
        }
        /* AKILLI YANIT */
        .smart-answer {
            background: var(--card);
            border: 1.5px solid #ddd6fe;
            border-left: 4px solid var(--accent);
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 28px;
            box-shadow: var(--shadow);
        }
        .smart-answer-label {
            font-size: 11px;
            font-weight: 700;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        .smart-answer-text {
            font-size: 18px;
            font-weight: 600;
            color: var(--text);
        }
        /* SONUÇ KARTI */
        .result-item {
            padding: 18px 0;
            border-bottom: 1px solid var(--border);
        }
        .result-item:last-child { border-bottom: none; }
        .result-domain {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
        }
        .result-favicon {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            background: var(--border);
        }
        .result-url-text {
            font-size: 13px;
            color: var(--url-color);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 500px;
        }
        .result-title {
            font-size: 19px;
            font-weight: 600;
            margin-bottom: 5px;
            line-height: 1.3;
        }
        .result-title a {
            color: #1d4ed8;
            text-decoration: none;
        }
        .result-title a:hover {
            text-decoration: underline;
        }
        .result-snippet {
            font-size: 14px;
            color: #374151;
            line-height: 1.6;
        }
        .result-snippet mark {
            background: #fef08a;
            color: var(--text);
            border-radius: 2px;
            padding: 0 2px;
        }
        /* BOŞ SONUÇ */
        .no-result {
            text-align: center;
            padding: 60px 20px;
            color: var(--muted);
        }
        .no-result-icon { font-size: 40px; margin-bottom: 12px; }
        .no-result-title { font-size: 18px; font-weight: 600; color: var(--text); margin-bottom: 8px; }
        /* ADMIN */
        .admin-section {
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }
        .admin-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
        }
        .admin-form { display: flex; gap: 8px; }
        .admin-input {
            flex: 1;
            border: 1.5px solid var(--border);
            background: var(--card);
            padding: 9px 14px;
            border-radius: 8px;
            font-size: 14px;
            color: var(--text);
            outline: none;
            transition: border-color 0.15s;
        }
        .admin-input:focus { border-color: var(--accent); }
        .admin-btn {
            background: var(--text);
            color: white;
            border: none;
            padding: 9px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.15s;
        }
        .admin-btn:hover { opacity: 0.8; }
        @media (max-width: 600px) {
            .results-header { padding: 12px 16px; gap: 12px; }
            .results-body { padding: 20px 16px; }
            .result-title { font-size: 17px; }
        }
    </style>
</head>
<body>
{% if not sorgu %}
<div class="home-page">
    <div class="home-logo">Zedin.</div>
    <div class="home-search">
        <form method="GET" action="/">
            <div class="search-wrap">
                <input type="text" name="q" class="search-input" placeholder="Ara..." autocomplete="off" autofocus>
                <button type="submit" class="search-btn">Ara</button>
            </div>
        </form>
    </div>
</div>
{% else %}
<header class="results-header">
    <a href="/" class="results-logo">Zedin.</a>
    <form method="GET" action="/" style="flex:1; max-width:560px;">
        <div class="search-wrap">
            <input type="text" name="q" class="search-input" value="{{ sorgu }}" autocomplete="off" autofocus>
            <button type="submit" class="search-btn">Ara</button>
        </div>
    </form>
</header>
<div class="results-body">
    {% if hizi is not none %}
        <div class="metrics">
            {{ sonuclar|length }} sonuç &mdash; {{ "%.3f"|format(hizi) }} saniye
        </div>
    {% endif %}
    {% if snippet_sonuc %}
        <div class="smart-answer">
            <div class="smart-answer-label">Hızlı Yanıt</div>
            <div class="smart-answer-text">{{ snippet_sonuc }}</div>
        </div>
    {% endif %}
    {% if sonuclar %}
        {% for satir in sonuclar %}
            <div class="result-item">
                <div class="result-domain">
                    <img class="result-favicon" src="https://www.google.com/s2/favicons?domain={{ satir[0] }}&sz=16" onerror="this.style.display='none'" alt="">
                    <span class="result-url-text">{{ satir[0] }}</span>
                </div>
                <h3 class="result-title">
                    <a href="{{ satir[0] }}" target="_blank" rel="noopener">{{ satir[1] }}</a>
                </h3>
                <p class="result-snippet">{{ satir[2][:220] }}...</p>
            </div>
        {% endfor %}
    {% elif not snippet_sonuc %}
        <div class="no-result">
            <div class="no-result-icon">🔍</div>
            <div class="no-result-title">Sonuç bulunamadı</div>
            <p>{{ sorgu }} için herhangi bir sonuç bulunamadı.</p>
        </div>
    {% endif %}
    <div class="admin-section">
        <div class="admin-label">Siteyi İndeksle</div>
        <form method="POST" action="/ekle" class="admin-form">
            <input type="text" name="yeni_url" class="admin-input" placeholder="https://ornek.com.tr">
            <button type="submit" class="admin-btn">Ekle</button>
        </form>
    </div>
</div>
{% endif %}
</body>
</html>
"""

def snippet_kontrol(sorgu):
    if re.match(r"^[0-9\s\+\-\*\/\(\)\.]+$", sorgu):
        try:
            return f"{sorgu} = {eval(sorgu)}"
        except:
            pass
    if sorgu.lower() in ["sa", "selam", "merhaba"]:
        return "Merhaba! Zedin Arama Motoruna hoş geldiniz."
    return None

def alakali_mi(sorgu_kelimeleri, baslik, icerik):
    metin = (baslik + " " + icerik).lower()
    for kelime in sorgu_kelimeleri:
        if len(kelime) > 2 and kelime not in metin:
            return False
    return True

@app.route("/")
def ara():
    sorgu = request.args.get("q", "").strip()
    sonuclar = []
    snippet_sonuc = snippet_kontrol(sorgu) if sorgu else None
    arama_suresi = None                                 
    if sorgu and not snippet_sonuc:
        baslangic = time.perf_counter()
        sorgu_kelimeleri = [k.lower() for k in sorgu.split() if len(k) > 1]
        
        conn = sqlite3.connect("lokal_arama.db")
        cursor = conn.cursor()
        try:
            fts_sorgu = " OR ".join([f'"{k}"*' for k in sorgu_kelimeleri])
            cursor.execute("""
                SELECT url, baslik, icerik
                FROM sayfalar
                WHERE sayfalar MATCH ?
                ORDER BY bm25(sayfalar, 10.0, 0.0, 1.0) ASC
                LIMIT 50
            """, (fts_sorgu,))
            ham_sonuclar = cursor.fetchall()
            
            for satir in ham_sonuclar:
                if alakali_mi(sorgu_kelimeleri, satir[1] or "", satir[2] or ""):
                    sonuclar.append(satir)
                if len(sonuclar) >= 20:
                    break
        except Exception as e:
            print(f"[!] Arama hatasi: {e}")
        finally:
            conn.close()
        arama_suresi = time.perf_counter() - baslangic  
        
    return render_template_string(
        HTML_SABLON,
        sonuclar=sonuclar,
        sorgu=sorgu,
        snippet_sonuc=snippet_sonuc,
        hizi=arama_suresi
    )

# 🔒 [YENİ] SİTE EKLEME SINIRI: Botların sunucuyu şişirmesini önlemek için dakikada maks 3 istek hakkı
@app.route("/ekle", methods=["POST"])
@limiter.limit("3 per minute")
def ekle():
    hedef_url = request.form.get("yeni_url", "").strip()
    if hedef_url:
        link_ayıkla_ve_tarla(hedef_url, max_sayfa=50)
    return redirect(url_for("ara"))

if __name__ == "__main__":
    # 🌍 Railway entegrasyonu için sabit IP/Port yerine çevre değişkenlerini yakalayacak şekilde güncellendi
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

