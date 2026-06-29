import os
import math

HEDEF_DOSYA = "domainler.txt"
TEMIZ_DOSYA = "domainler_temiz.txt"

def shannon_entropi(metin):
    """Metnin rastgelelik (kaos) derecesini hesaplar. 
    Rastgele domainlerin entropisi her zaman çok yüksektir."""
    if not metin:
        return 0
    
    # Harf frekanslarını hesapla
    frekanslar = {}
    for karakter in metin:
        frekanslar[karakter] = frekanslar.get(karakter, 0) + 1
        
    # Entropi formülünü uygula
    entropi = 0
    toplam_karakter = len(metin)
    for sayi in frekanslar.values():
        olasilik = sayi / toplam_karakter
        entropi -= olasilik * math.log2(olasilik)
        
    return entropi

def domain_temiz_mi(domain):
    saf = domain.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0].lower()
    
    if not saf or "." not in saf:
        return False
        
    ana_isim = saf.split('.')[0]
    
    # Çok kısa veya çok uzunları doğrudan ele
    if len(ana_isim) < 3 or len(ana_isim) > 40:
        return False

    # 1. Adım: Entropi (Rastgelelik) Kontrolü
    # Normal anlamlı kelimelerin entropisi genelde 2.0 ile 3.6 arasındadır.
    # asdasd123, qweqwe, ax92j1 gibi yapılarda bu değer fırlar.
    entropi_degeri = shannon_entropi(ana_isim)
    
    # Eğer domain uzunsa ve harfler aşırı rastgele dağılmışsa çöptür
    if len(ana_isim) > 8 and entropi_degeri > 3.4:
        return False
        
    # Eğer domain kısaysa ama karakter çeşitliliği aşırı saçmaysa (örn: xq7)
    if len(ana_isim) <= 6 and entropi_degeri > 2.8 and any(c.isdigit() for c in ana_isim):
        return False

    # 2. Adım: Dil Kalıbı Kontrolü (Tekrarlayan Bloklar)
    # Yan yana gelen aynı karakterlerin veya kalıpların kontrolü
    for i in range(len(ana_isim) - 2):
        ucluu_blok = ana_isim[i:i+3]
        # Aynı harf 3 kere yan yana geldiyse (örn: www, aaa, sss)
        if len(set(ucluu_blok)) == 1:
            return False

    # 3. Adım: Sayı Yoğunluğu
    sayilar = sum(1 for c in ana_isim if c.isdigit())
    if sayilar > 3 and (sayilar / len(ana_isim)) > 0.35:
        return False

    return True

def filtrele():
    if not os.path.exists(HEDEF_DOSYA):
        print(f"[!] {HEDEF_DOSYA} bulunamadı!")
        return

    print("[*] Gelişmiş Bilgi Teorisi (Entropi) Filtresi Başlatıldı...")
    
    with open(HEDEF_DOSYA, "r", encoding="utf-8") as f:
        domainler = [satir.strip() for satir in f if satir.strip()]

    temiz_list = []
    elenecek_list = []

    for d in domainler:
        if domain_temiz_mi(d):
            temiz_list.append(d)
        else:
            elenecek_list.append(d)

    with open(TEMIZ_DOSYA, "w", encoding="utf-8") as f:
        for d in sorted(temiz_list):
            f.write(f"{d}\n")

    print(f"\n[+] Analiz Tamamlandı!")
    print(f"    Elenen Saçma/Kaotik Domain: {len(elenecek_list)}")
    print(f"    Kalan Kaliteli Domain     : {len(temiz_list)}")
    print(f"    Yeni liste '{TEMIZ_DOSYA}' olarak kaydedildi.")

if __name__ == "__main__":
    filtrele()

