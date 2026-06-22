import time
import os
import json
from datetime import datetime
from tarayici import link_ayıkla_ve_tarla, veritabani_olustur

DOMAIN_LISTESI = "domainler.txt"
ILERLEME_DOSYASI = "toplu_ilerleme.json"
MAX_SAYFA_PER_SITE = 500  # Her site icin max sayfa

def ilerlemeyi_yukle() -> set:
    if os.path.exists(ILERLEME_DOSYASI):
        with open(ILERLEME_DOSYASI, "r") as f:
            return set(json.load(f))
    return set()

def ilerlemeyi_kaydet(tamamlananlar: set):
    with open(ILERLEME_DOSYASI, "w") as f:
        json.dump(list(tamamlananlar), f)

def domainleri_yukle() -> list:
    if not os.path.exists(DOMAIN_LISTESI):
        print(f"[!] {DOMAIN_LISTESI} bulunamadi!")
        exit(1)
    with open(DOMAIN_LISTESI, "r") as f:
        return [s.strip() for s in f if s.strip().startswith("http")]

if __name__ == "__main__":
    print("=" * 55)
    print("  Zedin Toplu Tarayici v1.0")
    print("=" * 55)

    veritabani_olustur()

    domainler = domainleri_yukle()
    tamamlananlar = ilerlemeyi_yukle()

    kalan = [d for d in domainler if d not in tamamlananlar]

    print(f"[*] Toplam domain  : {len(domainler)}")
    print(f"[*] Tamamlanan     : {len(tamamlananlar)}")
    print(f"[*] Kalan          : {len(kalan)}")
    print(f"[*] Site basi max  : {MAX_SAYFA_PER_SITE} sayfa")
    print("=" * 55)

    baslangic_zamani = time.time()

    for i, domain in enumerate(kalan, 1):
        print(f"\n[{i}/{len(kalan)}] Taranıyor: {domain}")
        try:
            link_ayıkla_ve_tarla(domain, max_sayfa=MAX_SAYFA_PER_SITE)
            tamamlananlar.add(domain)
            ilerlemeyi_kaydet(tamamlananlar)
        except KeyboardInterrupt:
            print("\n[!] Kullanici tarafindan durduruldu!")
            print(f"[*] Ilerleme kaydedildi: {len(tamamlananlar)} site tamamlandi.")
            break
        except Exception as e:
            print(f"[!] {domain} hatasi: {e}")
            tamamlananlar.add(domain)  # Hatali siteyi de tamamlandi say, tekrar deneme
            ilerlemeyi_kaydet(tamamlananlar)
            continue

        gecen = time.time() - baslangic_zamani
        kalan_site = len(kalan) - i
        ortalama = gecen / i
        tahmini = ortalama * kalan_site

        print(f"[*] Gecen sure    : {gecen/60:.1f} dk")
        print(f"[*] Tahmini kalan : {tahmini/60:.1f} dk")
        print(f"[*] Tamamlanan    : {len(tamamlananlar)}/{len(domainler)}")

    print("\n" + "=" * 55)
    print(f"[+] TAMAMLANDI! {len(tamamlananlar)} site indekslendi.")
    print("=" * 55)

    # Ilerleme dosyasini temizle
    if os.path.exists(ILERLEME_DOSYASI):
        os.remove(ILERLEME_DOSYASI)
