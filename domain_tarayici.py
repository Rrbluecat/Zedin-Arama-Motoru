import json
import os
import time
from datetime import datetime

try:
    import zedin_domain as zd
    print("[+] Rust motoru yuklendi!")
except ImportError:
    print("[!] Rust modulu bulunamadi!")
    exit(1)

DOMAIN_LISTESI = "domainler.txt"
CIKTI_JSON     = "turk_siteleri.json"
CIKTI_TXT      = "domainler.txt"
ILERLEME       = "tarayici_ilerleme.json"

def mevcut_domainleri_yukle() -> set:
    domainler = set()
    if os.path.exists(CIKTI_TXT):
        with open(CIKTI_TXT, "r") as f:
            for satir in f:
                satir = satir.strip()
                if satir:
                    domainler.add(satir.replace("https://", "").replace("http://", ""))
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

    print(f"[+] {len(domainler)} domain kaydedildi!")

if __name__ == "__main__":
    print("=" * 55)
    print("  Zedin Domain Tarayici v1.0 - Rust/PyO3")
    print("=" * 55)

    if not os.path.exists(DOMAIN_LISTESI):
        print(f"[!] {DOMAIN_LISTESI} bulunamadi! Once domain_avcisi.py calistir.")
        exit(1)

    # Mevcut domainleri yukle
    mevcut = mevcut_domainleri_yukle()
    print(f"[*] Mevcut domain sayisi: {len(mevcut)}")

    tur = 1
    while True:
        print(f"\n[*] TUR {tur} basliyor...")
        baslangic = time.time()

        # Rust ile tum domainleri tara
        yeni_domainler = set(zd.domain_listesini_tara(DOMAIN_LISTESI))

        # Yenileri mevcut listeye ekle
        onceki = len(mevcut)
        mevcut.update(yeni_domainler)
        eklenen = len(mevcut) - onceki
        sure = time.time() - baslangic

        print(f"\n[+] Tur {tur} tamamlandi!")
        print(f"    Yeni eklenen : {eklenen} domain")
        print(f"    Toplam       : {len(mevcut)} domain")
        print(f"    Sure         : {sure:.1f} saniye")

        # Kaydet
        sonuclari_kaydet(mevcut)

        if eklenen == 0:
            print("\n[*] Yeni domain bulunamadi, tarama tamamlandi!")
            break

        tur += 1
        print(f"[*] Sonraki tur icin 5 saniye bekleniyor...")
        time.sleep(5)
