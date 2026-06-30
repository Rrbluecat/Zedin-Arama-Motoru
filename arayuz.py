import os
import re
import json
import glob
import gzip
import threading
from flask import Flask, request, abort, jsonify
from flask_cors import CORS  # 🌐 Farklı portlardan (Next.js) erişim için şart!
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tarayici import link_ayıkla_ve_tarla

app = Flask(__name__)
CORS(app)  # Tüm kökenlerden (frontend) gelen isteklere izin veriyoruz

# 🔒 [KORUMA] DDOS KORUMASI: İndeks çekme limitleri
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"],  # Limit profesyonel bir API için esnetildi
    storage_uri="memory://"
)
KARA_LISTE_BOTLAR = ["sqlmap", "nikto", "dirbuster", "nmap", "python-requests"]

@app.before_request
def bot_kontrolu():
    user_agent = request.headers.get('User-Agent', '').lower()
    if any(bot in user_agent for bot in KARA_LISTE_BOTLAR):
        abort(403)

# 🚀 [SHARDING MİMARİSİ]
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

# 🚀 DOSYALARI RAM'E TOPLAMA MOTORU
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

# 🛰️ --- API ENDPOINT'LERİ ---
@app.route("/api/indeks", methods=["GET"])
def api_indeks():
    """Frontend'in shard veya tüm indeksi JSON olarak çekeceği ana damar"""
    harf = request.args.get("harf", "").lower()
    if harf and hasattr(ARAMA_INDEKSI, 'shards'):
        return jsonify(ARAMA_INDEKSI.shards.get(harf, []))
    return jsonify(ARAMA_INDEKSI)

@app.route("/api/ekle", methods=["POST"])
@limiter.limit("3 per minute")
def ekle():
    """Yeni URL ekleme isteği artık JSON dönecek, yönlendirme (redirect) yapmayacak"""
    veri = request.get_json() or {}
    hedef_url = veri.get("yeni_url", "").strip()

    if not hedef_url:
        return jsonify({"durum": "hata", "mesaj": "URL boş olamaz"}), 400

    # Arka planda taramayı başlat (Thread kullanarak Flask'ı kilitlemiyoruz)
    threading.Thread(
        target=link_ayıkla_ve_tarla,
        args=(hedef_url,),
        kwargs={"max_sayfa": 250, "eszamanli_isci": 5}
    ).start()

    return jsonify({"durum": "basarili", "mesaj": f"{hedef_url} için tarama arka planda başlatıldı."})

@app.route("/api/otomatik-besle", methods=["GET"])
def otomatik_besle_tetikle():
    from tarayici import zedin_otomatik_besleme
    thread = threading.Thread(target=zedin_otomatik_besleme)
    thread.start()
    return jsonify({"durum": "basarili", "mesaj": "Zedin paralel örümcekleri arka planda uyandı!"})

if __name__ == "__main__":
    # 🚨 PORT KRİZİNİ ÇÖZEN DEĞİŞİKLİK:
    # Railway'in dış PORT değişkenini Next.js'e bırakıyoruz.
    # Flask içeride tamamen izole bir şekilde 5000 portuna çekiliyor.
    app.run(host="127.0.0.1", port=5000, debug=False)

