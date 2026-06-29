import os

GECICI_LISTE = "temiz_domainler.tmp"
HEDEF_DOSYA = "domainler.txt"

def hedefe_kaydet():
    if not os.path.exists(GECICI_LISTE):
        print(f"[!] {GECICI_LISTE} bulunamadı! Önce ilk scripti çalıştırın.")
        return

    print(f"[*] Veriler {HEDEF_DOSYA} dosyasına yazılıyor...")
    
    # Eğer önceden kalma bir hedef dosya varsa mevcutları korumak için yükleyelim
    mevcut_domainler = set()
    if os.path.exists(HEDEF_DOSYA):
        with open(HEDEF_DOSYA, "r", encoding="utf-8") as f:
            for satir in f:
                if satir.strip():
                    mevcut_domainler.add(satir.strip())

    # Yeni eklenenleri de üzerine katalım
    with open(GECICI_LISTE, "r", encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                mevcut_domainler.add(satir.strip())

    # Hepsini tek seferde sıralı olarak ana hedef dosyana yazalım
    with open(HEDEF_DOSYA, "w", encoding="utf-8") as f:
        for domain in sorted(mevcut_domainler):
            f.write(f"{domain}\n")

    # İşimiz bitince geçici dosyayı temizleyelim
    if os.path.exists(GECICI_LISTE):
        os.remove(GECICI_LISTE)

    print(f"[+] İŞLEM TAMAMLANDI! {HEDEF_DOSYA} güncellendi. Toplam güncel domain sayısı: {len(mevcut_domainler)}")

if __name__ == "__main__":
    hedefe_kaydet()

