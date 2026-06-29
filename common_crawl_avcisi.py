import os
import re
import gzip
import requests
import json
import random
from datetime import datetime

# Zedin'in hedeflediği uzantıların regex deseni
UZANTI_REGEX = re.compile(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com\.tr|edu\.tr|org\.tr|gov\.tr|net\.tr|com|edu|tr))', re.IGNORECASE)

CIKTI_TXT = "domainler.txt"
CIKTI_JSON = "turk_siteleri.json"

def mevcut_domainleri_yukle() -> set:
    domainler = set()
    if os.path.exists(CIKTI_TXT):
        with open(CIKTI_TXT, "r", encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                if satir:
                    # Temizleme işlemi
                    d = satir.replace("https://", "").replace("http://", "").split('/')[0]
                    domainler.add(d)
    return domainler

def sonuclari_kaydet(domainler: set):
    veri = {
        "olusturulma_tarihi": datetime.now().isoformat(),
        "toplam_domain": len(domainler),
        "domainler": sorted(domainler)
    }
    with open(CIKTI_JSON, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

    with open(CIKTI_TXT, "w", encoding="utf-8") as f:
        for d in sorted(domainler):
            f.write(f"https://{d}\n")
    print(f"[+] Toplam {len(domainler)} domain başarıyla senkronize edildi.")

def cc_uzanti_avcisi(limit_satir=1500000):
    """
    Common Crawl CDX URL indekslerinden rastgele bir parçayı (shard) alır,
    satır satır okuyarak hedef uzantılı domainleri Zedin'e katar.
    """
    print("=" * 55)
    print("  Zedin - Common Crawl CDX İndeks Filtreleyici")
    print("=" * 55)

    mevcut = mevcut_domainleri_yukle()
    print(f"[*] Başlangıçta mevcut domain sayısı: {len(mevcut)}")

    # Common Crawl verisi 300 parçaya (00000 - 00299) bölünmüştür. 
    # Her çalıştırmada rastgele birini seçerek internetin farklı bir köşesini tararız.
    rastgele_shard = random.randint(0, 299)
    cc_url = f"https://data.commoncrawl.org/cc-index/collections/CC-MAIN-2024-10/indexes/cdx-{rastgele_shard:05d}.gz"
    
    print(f"[*] Rastgele CDX Havuzu ({rastgele_shard}/299) taranıyor: {cc_url}")
    print("[*] Bu işlem doğrudan stream ediliyor, lütfen bekleyin...")

    try:
        response = requests.get(cc_url, stream=True, timeout=30)
        if response.status_code != 200:
            print(f"[!] Bağlantı hatası: {response.status_code}")
            return

        # Gzip içeriğini açarak satır satır okuma
        with gzip.GzipFile(fileobj=response.raw) as f:
            sayac = 0
            eklenen = 0

            for line in f:
                # Satırları çözümle. CDX formatı JSON benzeri parçalar içerir.
                satir_metni = line.decode('utf-8', errors='ignore').strip()
                sayac += 1
                
                # Regex ile JSON formatlı verinin içindeki URL kısmından domaini çekiyoruz
                eslesme = UZANTI_REGEX.search(satir_metni)
                if eslesme:
                    domain = eslesme.group(1).lower()
                    if domain not in mevcut:
                        mevcut.add(domain)
                        eklenen += 1

                if sayac % 100000 == 0:
                    print(f"[-] {sayac} URL satırı incelendi... Bulunan yeni domain: {eklenen}")

                if sayac >= limit_satir:
                    print(f"[!] Limit sınıra ulaşıldı ({limit_satir} satır).")
                    break

        print(f"\n[+] Tarama tamamlandı. Bu turda {eklenen} yeni benzersiz domain keşfedildi!")
        sonuclari_kaydet(mevcut)

    except Exception as e:
        print(f"[!] Common Crawl verisi işlenirken hata oluştu: {e}")

if __name__ == "__main__":
    cc_uzanti_avcisi()

