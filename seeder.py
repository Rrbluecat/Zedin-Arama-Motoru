import requests
from bs4 import BeautifulSoup
from tarayici import link_ayıkla_ve_tarla

# Zedin'in her gün otomatik olarak sömüreceği dev başlangıç listesi
HAZIR_KAYNAKLAR = [
    "https://evrimagaci.org/sitemap.xml",
    "https://www.webtekno.com/sitemap.xml",
    "https://www.donanimhaber.com/sitemap.xml",
    # Buraya istediğin kadar büyük sitenin sitemap adresini ekleyebilirsin
]

def sitemap_linklerini_topla(sitemap_url):
    print(f"[{sitemap_url}] adresinden linkler fışkırtılıyor...")
    try:
        res = requests.get(sitemap_url, headers={'User-Agent': 'ZedinBot/2.0'}, timeout=5)
        soup = BeautifulSoup(res.text, 'xml') # XML olarak okuyoruz
        
        # XML içindeki <loc> etiketleri doğrudan alt sayfaların linkleridir
        linkler = [loc.text for loc in soup.find_all('loc')]
        print(f"-> Başarıyla {len(linkler)} adet temiz alt sayfa linki çekildi!")
        return linkler
    except Exception as e:
        print(f"Sitemap okunurken hata çıktı: {e}")
        return []

if __name__ == "__main__":
    print("=== ZEDİN TOPLU BESLEME MOTORU ===")
    
    tum_kuyruk = []
    for kaynak in HAZIR_KAYNAKLAR:
        linkler = sitemap_linklerini_topla(kaynak)
        tum_kuyruk.extend(linkler[:50]) # Her siteden ilk aşamada en kaliteli 50 linki alalım
        
    print(f"\nToplam {len(tum_kuyruk)} adet nokta atışı link havuzu hazırlandı.")
    print("Şimdi Zedin Örümceği bu link havuzunu yüksek hızda veritabanına işleyecek...\n")
    
    # Topladığımız temiz linkleri ana örümceğe paslıyoruz
    for sira, url in enumerate(tum_kuyruk, 1):
        print(f"\n[SIRA {sira}/{len(tum_kuyruk)}] Hedef taranıyor: {url}")
        # max_sayfa=1 diyoruz çünkü zaten nokta atışı alt sayfa linkini verdik, içeride dolanmasına gerek yok
        link_ayıkla_ve_tarla(url, max_sayfa=1)

    print("\n=== TOPLU İNDEKSLEME BİTTİ! ZEDİN COŞTU ===")

