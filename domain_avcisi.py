import json
import os
import time
from datetime import datetime

# Rust modülünü import et
try:
    import zedin_domain as zd
    RUST_AKTIF = True
    print("[+] Rust motoru yüklendi!")
except ImportError:
    RUST_AKTIF = False
    print("[!] Rust modülü bulunamadı, önce 'maturin develop --release' çalıştır!")
    exit(1)

CIKTI_JSON = "turk_siteleri.json"
CIKTI_TXT  = "domainler.txt"
ILERLEME   = "ilerleme.json"

def ilerlemeyi_yukle() -> set:
    if os.path.exists(ILERLEME):
        with open(ILERLEME, 'r') as f:
            return set(json.load(f))
    return set()

def ilerlemeyi_kaydet(domainler: set):
    with open(ILERLEME, 'w') as f:
        json.dump(list(domainler), f)

def sonuclari_kaydet(domainler: set):
    veri = {
        "olusturulma_tarihi": datetime.now().isoformat(),
        "toplam_domain": len(domainler),
        "domainler": sorted(domainler)
    }
    with open(CIKTI_JSON, 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

    with open(CIKTI_TXT, 'w', encoding='utf-8') as f:
        for d in sorted(domainler):
            f.write(f"https://{d}\n")

    print(f"[+] {len(domainler)} domain kaydedildi → {CIKTI_JSON} & {CIKTI_TXT}")

if __name__ == "__main__":
    print("=" * 55)
    print("  Zedin Domain Avcısı v4.0 - Rust/PyO3 Hibrit")
    print("=" * 55)

    onceki = ilerlemeyi_yukle()
    if onceki:
        print(f"[~] Önceki oturumdan {len(onceki)} domain yüklendi.")

    baslangic = time.time()

    # Rust motoru tüm işi yapıyor
    print("[*] Rust paralel tarama motoru başlatılıyor...")
    rust_domainler = zd.tum_domainleri_topla()

    tum_domainler = onceki | set(rust_domainler)
    ilerlemeyi_kaydet(tum_domainler)

    sure = time.time() - baslangic
    print(f"\n{'='*55}")
    print(f"[+] TAMAMLANDI! {len(tum_domainler)} benzersiz domain!")
    print(f"[+] Süre: {sure/60:.1f} dakika")
    print(f"{'='*55}")

    sonuclari_kaydet(tum_domainler)

    if os.path.exists(ILERLEME):
        os.remove(ILERLEME)

