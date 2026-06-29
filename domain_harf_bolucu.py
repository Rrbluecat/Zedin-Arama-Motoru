import os
from datetime import datetime

HEDEF_DOSYA = "domainler.txt"
CIKIS_KLASORU = "harfler"

def harf_harf_bol_ve_sirala():
    if not os.path.exists(HEDEF_DOSYA):
        print(f"[!] {HEDEF_DOSYA} bulunamadı! Önce filtreleme scriptini çalıştırın.")
        return

    # Harf dosyalarını toplayacağımız klasörü otomatik oluştur
    if not os.path.exists(CIKIS_KLASORU):
        os.makedirs(CIKIS_KLASORU)

    print("=" * 60)
    print(" 🗂️  ZEDIN DOMAIN HARF BÖLÜCÜ VE SIRALAYICI SİSTEMİ")
    print("=" * 60)
    print(f"[*] '{HEDEF_DOSYA}' okunuyor ve harf havuzlarına dağıtılıyor...\n")

    okunan_satir = 0
    dagitilan_sayi = 0
    baslangic_zamani = datetime.now()

    # Bellek dostu ve hızlı işlem için domainleri önce RAM'deki harf sözlüklerinde grupluyoruz
    havuzlar = {}

    with open(HEDEF_DOSYA, "r", encoding="utf-8", errors="ignore") as kaynak:
        for satir in kaynak:
            okunan_satir += 1
            domain = satir.strip().lower()
            if not domain: 
                continue

            # Domainin ilk karakterini (baş harfini) yakala
            bas_harf = domain[0]

            # Eğer baş harf sayı veya sembol ise hepsini tek bir 'numara_sembol' havuzuna at
            if not bas_harf.isalpha():
                bas_harf = "numara_sembol"

            if bas_harf not in havuzlar:
                havuzlar[bas_harf] = []

            havuzlar[bas_harf].append(domain)

            if okunan_satir % 100000 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {okunan_satir} domain tasnif edildi...")

    print("\n[*] Tasnif bitti. Domainler alfabetik sıralanarak dosyalara yazılıyor...")
    
    # Her harf havuzunu kendi içinde A'dan Z'ye sıralayıp diske yazıyoruz
    for harf, domain_listesi in havuzlar.items():
        dosya_yolu = os.path.join(CIKIS_KLASORU, f"{harf}.txt")
        
        # sorted() fonksiyonu sayesinde dosyanın içi de tamamen alfabetik olur
        sirali_liste = sorted(domain_listesi)
        
        with open(dosya_yolu, "w", encoding="utf-8") as hedef:
            for d in sirali_liste:
                hedef.write(f"{d}\n")
                dagitilan_sayi += 1

    gecen_sure = datetime.now() - baslangic_zamani
    print("\n" + "=" * 60)
    print("[+] BÖLME VE ALFABETİK SIRALAMA İŞLEMİ TAMAMLANDI!")
    print(f"    Tasnif Edilen Toplam Domain : {dagitilan_sayi}")
    print(f"    Oluşturulan Harf Dosyası    : {len(havuzlar)} adet")
    print(f"    Çıktıların Bulunduğu Klasör : /{CIKIS_KLASORU}")
    print(f"    Toplam Harcanan Süre        : {gecen_sure.seconds} saniye")
    print("=" * 60)

if __name__ == "__main__":
    harf_harf_bol_ve_sirala()

