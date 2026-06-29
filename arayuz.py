import os
import re
import json
import glob
import gzip
import threading
from flask import Flask, request, redirect, url_for, abort, jsonify, render_template_string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tarayici import link_ayıkla_ve_tarla

# 🚀 HTML Tasarım şablonunu diğer dosyadan içe aktarıyoruz
from sablonlar import HTML_SABLON

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

# 🚀 [YENİ SHARDING SIFINIF MİMARİSİ]
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
                if ilk.isalnum(): 
                    harf = ilk
            if harf not in self.shards: 
                self.shards[harf] = []
            if item not in self.shards[harf]: 
                self.shards[harf].append(item)

ARAMA_INDEKSI = ShardedIndexList()

# 🚀 [YENİ]: SIKIŞTIRILMIŞ (.json.gz) VE NORMAL (.json) DOSYALARI RAM'E TOPLAMA MOTORU
dosya_kaliplari = ["arama_indeksi_*.json", "arama_indeksi_*.json.gz", "arama_indeksi.json", "arama_indeksi.json.gz"]

for kalip in dosya_kaliplari:
    for dosya in glob.glob(kalip):
        try:
            if dosya.endswith(".gz"):
                with gzip.open(dosya, "rt", encoding="utf-8") as f:
                    veri = json.load(f)
            else:
                with open(dosya, "r", encoding="utf-8") as f:
                    veri = json.load(f)
            
            for v in veri:
                if v not in ARAMA_INDEKSI:
                    ARAMA_INDEKSI.append(v)
        except Exception as e:
            print(f"[!] {dosya} yüklenirken hata oluştu: {e}")

print(f"[*] Toplam {len(ARAMA_INDEKSI)} döküman bellek havuzuna güvenle yüklendi.")

@app.route("/")
def ara():
    return render_template_string(HTML_SABLON)

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
        link_ayıkla_ve_tarla(hedef_url, max_sayfa=250, eszamanli_isci=5)
    return redirect(url_for("ara"))

@app.route("/zedin-sihirbazini-uyandir-99")
def otomatik_besle_tetikle():
    from tarayici import zedin_otomatik_besleme
    thread = threading.Thread(target=zedin_otomatik_besleme)
    thread.start()
    return "Zedin paralel örümcekleri canlı sunucu açıkken arka planda çalışmaya başladı!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

