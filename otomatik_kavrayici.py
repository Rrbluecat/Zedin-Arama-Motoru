import sqlite3
from tarayici import link_ayıkla_ve_tarla

# Zedin'in keşfetmesi için Türkiye'nin en büyük 50 haber ve eğitim portalının ana sayfaları
TOHUM_LISTESI = [
    "https://www.google.com/search?q=site:.tr+haber",
    "https://www.yok.gov.tr/universiteler",
    "https://www.meb.gov.tr",
    # ... buraya 20-30 tane ana kategori portalı ekle
]

def zedin_otomatik_besleme():
    print("Zedin kendi kendini büyütmeye başladı...")
    for ana_site in TOHUM_LISTESI:
        print(f"Keşfediliyor: {ana_site}")
        # max_sayfa=500 vererek Zedin'in o site içindeki 
        # derinliklere inip linkleri kendi bulmasını sağlıyoruz
        link_ayıkla_ve_tarla(ana_site, max_sayfa=500)

if __name__ == "__main__":
    zedin_otomatik_besleme()

