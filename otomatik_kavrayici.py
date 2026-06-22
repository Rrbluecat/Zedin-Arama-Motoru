import os
import time
import random
from tarayici import link_ayıkla_ve_tarla

# Zedin'in bot engellerine takılmadan, derinlemesine temiz veri çekebileceği
# Türkiye'nin en köklü eğitim, bilim, kültür ve haber portalları
TOHUM_LISTESI = [
    # --- Yüksek Otoriteli Devlet & Eğitim Kurumları ---
    "https://www.meb.gov.tr",
    "https://www.yok.gov.tr",
    "https://www.osym.gov.tr",
    "https://www.eba.gov.tr",
    "https://www.tubitak.gov.tr",
    "https://dergipark.org.tr",
    
    # --- Önde Gelen Üniversiteler (Akademik Bilgi Havuzu) ---
    "https://www.itu.edu.tr",
    "https://www.odtu.edu.tr",
    "https://www.bogazici.edu.tr",
    "https://www.istanbul.edu.tr",
    "https://www.ankara.edu.tr",
    "https://www.hacettepe.edu.tr",
    "https://www.gazi.edu.tr",
    "https://www.anadolu.edu.tr",
    
    # --- Resmi Ajanslar ve Büyük Haber Portalları ---
    "https://www.aa.com.tr",
    "https://www.trthaber.com",
    "https://www.dhainternational.com",
    "https://www.ihaworlnews.com",
    
    # --- Kültür, Tarih ve Ansiklopedik Portallar ---
    "https://www.ttk.gov.tr",  # Türk Tarih Kurumu
    "https://www.tdk.gov.tr",  # Türk Dil Kurumu
    "https://www.kvmgm.gov.tr", # Kültür Varlıkları ve Müzeler Genel Müd.
    "https://www.bilimgenc.tubitak.gov.tr",
    
    # --- Doğruluk Kontrolü & Fact-Checking (Zedin'in Ana Damarı) ---
    "https://teyit.org",
    "https://www.dogrulukpayi.com",
    "https://www.malumatfurus.org",
    "https://www.dogrula.org"
]

def zedin_otomatik_besleme():
    print("\n=======================================================")
    print("🚀 ZEDIN CANLI OTOMATİK BESLEME MOTORU BAŞLATILDI 🚀")
    print("=======================================================\n")
    
    # Hedef listeyi karıştırarak her çalıştırmada farklı bir rotadan gitmesini sağlıyoruz
    # Bu işlem bot gibi davranıp sitelerden ban yeme riskini azaltır
    karisik_tohumlar = list(TOHUM_LISTESI)
    random.shuffle(karisik_tohumlar)
    
    toplam_taranan_ana_site = 0
    
    for sira, ana_site in enumerate(karisik_tohumlar, 1):
        print(f"\n[Sıra: {sira}/{len(karisik_tohumlar)}] Keşif Başlıyor: {ana_site}")
        
        try:
            # Sunucuyu yormamak ve canlı trafiği aksatmamak adına 
            # max_sayfa sınırını ideal seviyede (300) tutuyoruz.
            # tarayici.py artık atomik JSON yazma yaptığı için canlıda çökme yaşanmaz.
            link_ayıkla_ve_tarla(ana_site, max_sayfa=300)
            toplam_taranan_ana_site += 1
            
            # Sunucu açıkken siteler arası geçişte 5 saniye dinlenerek
            # Railway CPU limitlerini ve hedef sitelerin firewall'larını aşmıyoruz.
            print("[Uyu] Sunucu sağlığı ve IP koruması için 5 saniye bekleniyor...")
            time.sleep(5)
            
        except Exception as e:
            print(f"[!] {ana_site} taranırken bir aksama oldu, sıradaki siteye geçiliyor: {e}")
            continue

    print(f"\n🎉 [GÖREV TAMAMLANDI] Toplam {toplam_taranan_ana_site} ana portal ve alt kırılımları indekslendi!")

if __name__ == "__main__":
    zedin_otomatik_besleme()

