import os

HEDEF_DOSYA = "domainler.txt"
TEMIZ_DOSYA = "domainler_temiz.txt"

def sesli_sessiz_orani(metin):
    """Domain içindeki sesli ve sessiz harf dengesini kontrol eder."""
    sesli = set("aeıioöuü")
    harfler = [c for c in metin if c.isalpha()]
    if not harfler:
        return 0
    sesli_sayisi = sum(1 for c in harfler if c in sesli)
    return sesli_sayisi / len(harfler)

def ardisik_kontrol(metin):
    """Aşırı ardışık sessiz harf veya sayı bloklarını yakalar (örn: rstgwq, 182397)."""
    sessiz_blok = max((len(g) for g in "".join(c if c not in "aeıioöuü" and c.isalpha() else " " for c in metin).split()), default=0)
    sayi_blok = max((len(g) for g in "".join(c if c.isdigit() else " " for c in metin).split()), default=0)
    return max(sessiz_blok, sayi_blok)

def domain_skorla(domain):
    """Domainin çöp olup olmadığını matematiksel olarak hesaplar."""
    saf = domain.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0].lower()
    
    # Nokta içermeyen ya da tamamen boş kalan satırları ele
    if not saf or "." not in saf:
        return False
        
    ana_isim = saf.split('.')[0]
    
    if len(ana_isim) < 3:
        return False
        
    # Kural 1: Klavye random karakter analizi (asdasd, qweqwe vb.)
    random_kelimeler = ["asdasd", "qweqwe", "dfgh", "hjkl", "zxcv"]
    if any(r in ana_isim for r in random_kelimeler):
        return False
        
    # Kural 2: Sesli harf dengesi
    s_orani = sesli_sessiz_orani(ana_isim)
    if len(ana_isim) > 5 and (s_orani < 0.15 or s_orani > 0.85):
        return False
        
    # Kural 3: Ardışık karakter yığılması
    if ardisik_kontrol(ana_isim) > 4:
        return False
        
    # Kural 4: Aşırı uzun anlamsız sayılar
    sayi_sayisi = sum(1 for c in ana_isim if c.isdigit())
    if sayi_sayisi > 0 and (sayi_sayisi / len(ana_isim)) > 0.4:
        return False
        
    return True

def filtrele():
    if not os.path.exists(HEDEF_DOSYA):
        print(f"[!] {HEDEF_DOSYA} bulunamadı!")
        return

    print("[*] Zedin Matematiksel Frekans Filtresi çalışıyor (Kütüphanesiz)...")
    
    with open(HEDEF_DOSYA, "r", encoding="utf-8") as f:
        domainler = [satir.strip() for satir in f if satir.strip()]

    temiz_list = []
    elenecek_list = []

    for d in domainler:
        if domain_skorla(d):
            temiz_list.append(d)
        else:
            elenecek_list.append(d)

    # Temizlenenleri yaz
    with open(TEMIZ_DOSYA, "w", encoding="utf-8") as f:
        for d in sorted(temiz_list):
            f.write(f"{d}\n")

    print(f"\n[+] İşlem Tamamlandı!")
    print(f"    Elenen Çöp Domain Sayısı : {len(elenecek_list)}")
    print(f"    Kalan Temiz Domain Sayısı: {len(temiz_list)}")
    print(f"    Sonuçlar '{TEMIZ_DOSYA}' dosyasına kaydedildi.")

if __name__ == "__main__":
    filtrele()

