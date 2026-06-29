import os
import math
from datetime import datetime

HEDEF_DOSYA = "domainler.txt"
TEMIZ_DOSYA = "domainler_temiz.txt"

# KATMAN 1: Karaliste (Gereksiz küresel devleri ve çöpleri en başta elemek için)
KARA_LISTE = [
    "adclick", "doubleclick", "adsense", "analytics", "tracker",
    "affiliate", "casino", "bet", "kumar", "porn", "adult",
    "betting", "slot", "popup", "banner", "facebook", "instagram", 
    "twitter", "amazon", "netflix", "apple", "microsoft"
]

# Popüler Türkçe anahtar kelimeler (.com/.net siteleri yakalamak için)
TURKCE_ANAHTARLAR = [
    "haber", "sozcu", "milliyet", "hurriyet", "turk", "turkiye", 
    "indir", "film", "izle", "oyun", "bilgi", "kitap", "ders", 
    "okul", "universite", "forum", "blog", "gazete", "pazar", "magaza"
]

def shannon_entropi(metin):
    if not metin: return 0
    frekanslar = {}
    for karakter in metin:
        frekanslar[karakter] = frekanslar.get(karakter, 0) + 1
    entropi = 0
    toplam_karakter = len(metin)
    for sayi in frekanslar.values():
        olasilik = sayi / toplam_karakter
        entropi -= olasilik * math.log2(olasilik)
    return entropi

def domain_to_vector(ana_isim):
    alfabe = "abcdefghijklmnopqrstuvwxyz0123456789-"
    vektor = [0] * len(alfabe)
    for karakter in ana_isim:
        if karakter in alfabe:
            vektor[alfabe.index(karakter)] += 1
    toplam = sum(vektor)
    if toplam > 0:
        vektor = [v / toplam for v in vektor]
    return vektor

def kosinus_benzerligi(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0: return 0
    return dot_product / (norm_a * norm_b)

def hızlı_süzgeç(domain, ai_referanslar):
    # Protokol temizliği
    saf = domain.replace("https://", "").replace("http://", "").replace("www.", "").split('/')[0].lower()
    if not saf or "." not in saf: 
        return False
        
    ana_isim = saf.split('.')[0]
    
    # 1. Bariyer: Uzunluk ve Karaliste (İşlemciyi hiç yormayan statik kontrol)
    if len(ana_isim) < 3 or len(ana_isim) > 40: return False
    if any(k in ana_isim for k in KARA_LISTE): return False
    if any(r in ana_isim for r in ["asdasd", "qweqwe", "zxcv", "dfgh"]): return False

    # 2. Bariyer: Türkiye Odaklılık Kontrolü
    # Eğer .tr uzantılıysa veya içinde Türkçe anahtar kelime geçiyorsa direkt potaya girer
    is_turkish = saf.endswith(".tr") or any(k in ana_isim for k in TURKCE_ANAHTARLAR)
    if not is_turkish: 
        return False

    # 3. Bariyer: Karakter Dengesi ve Ardışık Yığılmalar
    sesli = set("aeıioöuü")
    harfler = [c for c in ana_isim if c.isalpha()]
    if harfler:
        s_orani = sum(1 for c in harfler if c in sesli) / len(harfler)
        if len(ana_isim) > 6 and (s_orani < 0.15 or s_orani > 0.85): return False

    sessiz_blok = max((len(g) for g in "".join(c if c not in "aeıioöuü" and c.isalpha() else " " for c in ana_isim).split()), default=0)
    sayi_blok = max((len(g) for g in "".join(c if c.isdigit() else " " for c in ana_isim).split()), default=0)
    if sessiz_blok > 4 or sayi_blok > 4: return False

    # 4. Bariyer: Matematiksel Kaos (Entropi)
    if len(ana_isim) > 8 and shannon_entropi(ana_isim) > 3.4: return False

    # 5. Bariyer: Yapay Zeka Semantik Vektör Analizi (En ağır katman, sadece yukarıyı geçenlere uygulanır)
    v = domain_to_vector(ana_isim)
    en_yuksek_benzerlik = max(kosinus_benzerligi(v, ref) for ref in ai_referanslar)
    if en_yuksek_benzerlik < 0.11: return False

    return True

def canavar_filtreyi_calistir():
    if not os.path.exists(HEDEF_DOSYA):
        print(f"[!] {HEDEF_DOSYA} bulunamadı! Lütfen önce kopyalamayı yapın.")
        return

    print("=" * 60)
    print(" ⚡ ZEDIN 1 MİLYON KAPASİTELİ AKIŞKAN FİLTRE MOTORU ⚡")
    print("=" * 60)
    print("[*] Analiz başlatıldı, bu işlem cihazı kilitlemeden arka planda akacaktır...\n")

    ai_referanslar = [
        domain_to_vector("teknoloji"), domain_to_vector("haberler"),
        domain_to_vector("universite"), domain_to_vector("bilgi-deposu")
    ]

    okunan_satir = 0
    temiz_sayisi = 0
    baslangic_zamani = datetime.now()

    # Streaming Modu: Okuma ve Yazma dosyalarını aynı anda açıp satır satır işliyoruz
    with open(HEDEF_DOSYA, "r", encoding="utf-8", errors="ignore") as kaynak, \
         open(TEMIZ_DOSYA, "w", encoding="utf-8") as hedef:
         
        for satir in kaynak:
            okunan_satir += 1
            satir_veri = satir.strip()
            if not satir_veri: continue
            
            # --- BAŞTAKİ KARAKTER/SIRA NO SIKINTISINI ÇÖZEN KISIM ---
            # Eğer satırda virgül varsa (Tranco CSV formatı), virgülden sonrasını (domaini) alıyoruz
            if "," in satir_veri:
                domain = satir_veri.split(',')[1]
            else:
                domain = satir_veri
            # --------------------------------------------------------

            # Filtreleme algoritması çalışıyor
            if hızlı_süzgeç(domain, ai_referanslar):
                hedef.write(f"{domain}\n")
                temiz_sayisi += 1

            # Her 50.000 satırda bir ekrana durum raporu bas (Canlı takip için)
            if okunan_satir % 50000 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] İşlenen: {okunan_satir} / 1.000.000 | Bulunan Temiz: {temiz_sayisi}")

    gecen_sure = datetime.now() - baslangic_zamani
    
    print("\n" + "=" * 60)
    print("[+] DEV FİLTRELEME İŞLEMİ BAŞARIYLA BİTTİ!")
    print(f"    Toplam İncelenen Satır  : {okunan_satir}")
    print(f"    Ayıklanan Temiz Türkiye : {temiz_sayisi}")
    print(f"    Elenen Çöp/Yabancı Site : {okunan_satir - temiz_sayisi}")
    print(f"    Toplam Harcanan Süre    : {gecen_sure.seconds} saniye")
    print(f"    Sonuçlar '{TEMIZ_DOSYA}' dosyasına kaydedildi.")
    print("=" * 60)

if __name__ == "__main__":
    canavar_filtreyi_calistir()

