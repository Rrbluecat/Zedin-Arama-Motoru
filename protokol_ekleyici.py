import os

HAM_LISTE = "ham_domainler.txt"
ISLENMIS_LISTE = "temiz_domainler.tmp"

def protokolleri_duzenle():
    if not os.path.exists(HAM_LISTE):
        print(f"[!] {HAM_LISTE} bulunamadı! Lütfen ham domainlerinizi bu dosyaya koyun.")
        return

    print("[*] Domain listesi okunuyor ve protokoller ekleniyor...")
    duzenlenmiş_domainler = set()

    with open(HAM_LISTE, "r", encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            
            # Eğer zaten protokol varsa elleme, yoksa https:// ekle
            if satir.startswith("http://") or satir.startswith("https://"):
                tam_url = satir
            else:
                tam_url = f"https://{satir}"
            
            duzenlenmiş_domainler.add(tam_url)

    # Geçici dosyaya yazalım, ikinci script burayı devralacak
    with open(ISLENMIS_LISTE, "w", encoding="utf-8") as f:
        for domain in sorted(duzenlenmiş_domainler):
            f.write(f"{domain}\n")

    print(f"[+] Başarılı! {len(duzenlenmiş_domainler)} domain işlendi ve geçici hafızaya alındı.")

if __name__ == "__main__":
    protokolleri_duzenle()

