import json
import os
import requests
import time
import urllib.parse
import glob
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from bs4 import BeautifulSoup
from optimizasyon import ZedinOptimizer

session = requests.Session()
session.headers.update({'User-Agent': 'ZedinBot/3.0 (Automated; +CommonCrawl Integration)'})
optimizer = ZedinOptimizer(benzerlik_esigi=5)

# Çoklu iş parçacığı (Multi-threading) için dosya ve RAM yazma kilidi
veri_kilidi = threading.Lock()

def veritabani_olustur():
    """Veritabanı ve tabloyu oluşturur, yoksa yaratır."""
    if not os.path.exists('arama_indeksi.json'):
        with open('arama_indeksi.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
        print("[DB] Veritabanı hazır.")

def common_crawl_url_kesfet(domain, limit=1000):
    """Common Crawl API'sini sorgulayarak hedef domaine ait arşivlenmiş derin URL'leri çeker."""
    print(f"[Common Crawl] '{domain}' için arşiv verileri sorgulanıyor...")
    kesfedilen_urller = set()
    
    # En güncel Common Crawl dizinlerinden örnekler
    cc_dizinleri = ["CC-MAIN-2025-18-index", "CC-MAIN-2024-51-index", "CC-MAIN-2024-38-index"]
    
    clean_domain = domain.replace("https://", "").replace("http://", "").split('/')[0]
    
    for dizin in cc_dizinleri:
        api_url = f"https://index.commoncrawl.org/{dizin}?url={clean_domain}/*&output=json&limit={limit}"
        try:
            response = requests.get(api_url, timeout=8)
            if response.status_code == 200:
                for line in response.text.strip().split('\n'):
                    if not line:
                        continue
                    try:
                        veri = json.loads(line)
                        if 'url' in veri:
                            kesfedilen_urller.add(veri['url'])
                    except:
                        continue
                if kesfedilen_urller:
                    print(f"[Common Crawl] {dizin} dizininden {len(kesfedilen_urller)} benzersiz kaynak yakalandı.")
                    break # Başarılı veri çekildiyse diğer dizinleri sorgulayıp vakit kaybetme
        except Exception as e:
            continue
            
    return list(kesfedilen_urller)

def tek_sayfa_tarla(url, baslangic_domain, tarandilar, kuyruk, mevcut_urller, sıkıstırılmıs_indeks, sayac_wrapper):
    """Çoklu iş parçacığı tarafından çağrılan bağımsız sayfa tarama işçisi."""
    url = optimizer.link_temizle(url)
    
    with veri_kilidi:
        if url in tarandilar:
            return
        tarandilar.add(url)

    try:
        response = session.get(url, timeout=6)
        if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
            return
            
        soup = BeautifulSoup(response.text, 'lxml')
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "svg"]):
            element.decompose()

        icerik = ' '.join(soup.get_text().split())
        if len(icerik) < 300:
            return
            
        if optimizer.kopya_icerik_mi(icerik, url=url):
            return
            
        baslik = soup.title.string.strip() if soup.title else url
        
        with veri_kilidi:
            if url in mevcut_urller:
                return
                
            # 🚀 [KALİTE İYİLEŞTİRMESİ]: Başlık 120, Özet içerik 350 karaktere çıkarılarak arama kalitesi maksimuma çıkartıldı.
            sayfa_verisi = [url, baslik[:120], icerik[:350]]
            sıkıstırılmıs_indeks.append(sayfa_verisi)
            mevcut_urller.add(url)
            sayac_wrapper['count'] += 1
            mevcut_sayac = sayac_wrapper['count']
            print(f"[{mevcut_sayac}] İndekslendi: {baslik[:50]}")

            # [SHARDING DISK SAVER]
            try:
                harf_anahtar = optimizer.harf_sec(baslik)
                shard_dosya = f'arama_indeksi_{harf_anahtar}.json'
                shard_listesi = []
                if os.path.exists(shard_dosya):
                    with open(shard_dosya, 'r', encoding='utf-8') as sf:
                        shard_listesi = json.load(sf)
                if sayfa_verisi not in shard_listesi:
                    shard_listesi.append(sayfa_verisi)
                    with open(shard_dosya, 'w', encoding='utf-8') as sf:
                        json.dump(shard_listesi, sf, ensure_ascii=False, separators=(',', ':'))
            except Exception as e:
                print(f"[SHARD YAZMA HATA] {e}")

            # [OTOMASYON CANLI GÜNCELLEME]
            try:
                import arayuz
                if sayfa_verisi not in arayuz.ARAMA_INDEKSI:
                    arayuz.ARAMA_INDEKSI.append(sayfa_verisi)
            except:
                pass

            # Global Dosya Commit Simülasyonu
            with open('arama_indeksi.json', 'w', encoding='utf-8') as f:
                json.dump(sıkıstırılmıs_indeks, f, ensure_ascii=False, separators=(',', ':'))

        # Yeni linkleri ayıkla ve kuyruğa at
        for a_etiketi in soup.find_all('a', href=True):
            link = a_etiketi['href']
            tam_link = urllib.parse.urljoin(url, link)
            tam_link = urllib.parse.urlsplit(tam_link)._replace(fragment="").geturl()
            tam_link = optimizer.link_temizle(tam_link)
            mevcut_domain = urllib.parse.urlsplit(tam_link).netloc
            
            if (tam_link.startswith('http') and mevcut_domain == baslangic_domain):
                kuyruk.put(tam_link)

    except Exception as e:
        pass

def link_ayıkla_ve_tarla(baslangic_url, max_sayfa=5000, eszamanli_isci=10):
    """Gelişmiş Çoklu İş Parçacıklı Otomatik Tarama Motoru."""
    tarandilar = set()
    kuyruk = Queue()
    kuyruk.put(baslangic_url)
    
    baslangic_domain = urllib.parse.urlsplit(baslangic_url).netloc
    sıkıstırılmıs_indeks = []
    mevcut_urller = set()
    sayac_wrapper = {'count': 0}

    # [SHARDING LOAD] Mükerrer kayıt engelleme
    for dosya in glob.glob('arama_indeksi_*.json'):
        try:
            with open(dosya, 'r', encoding='utf-8') as f:
                veriler = json.load(f)
                for veri in veriler:
                    if len(veri) > 0:
                        mevcut_urller.add(veri[0])
        except:
            pass

    if os.path.exists('arama_indeksi.json'):
        try:
            with open('arama_indeksi.json', 'r', encoding='utf-8') as f:
                sıkıstırılmıs_indeks = json.load(f)
                for veri in sıkıstırılmıs_indeks:
                    if len(veri) > 0:
                        mevcut_urller.add(veri[0])
        except:
            sıkıstırılmıs_indeks = []

    # 🚀 [YENİ]: Common Crawl Arşiv Keşif Aşaması Kuyruğa Enjekte Ediliyor
    cc_urlleri = common_crawl_url_kesfet(baslangic_domain, limit=max_sayfa)
    for cc_url in cc_urlleri:
        kuyruk.put(cc_url)

    # Çoklu iş parçacığı havuzu (Thread Pool) otomasyon başlatma
    print(f"[*] {eszamanli_isci} paralel işçi uyandırıldı. Tarama limitleri genişletildi.")
    
    with ThreadPoolExecutor(max_workers=eszamanli_isci) as executor:
        while sayac_wrapper['count'] < max_sayfa:
            try:
                # Kuyruktan veri bekle, 3 saniye içinde yeni link gelmezse döngüyü kontrol et
                url = kuyruk.get(timeout=3)
            except Empty:
                if kuyruk.empty():
                    break
                continue
                
            if url in tarandilar:
                kuyruk.task_done()
                continue
                
            executor.submit(
                tek_sayfa_tarla, url, baslangic_domain, tarandilar, 
                kuyruk, mevcut_urller, sıkıstırılmıs_indeks, sayac_wrapper
            )
            kuyruk.task_done()
            time.sleep(0.02) # Hedef sunucuyu çökertmemek için mini nefes payı

    print(f"\n[BİTTİ] Otomasyon tamamlandı. Toplam {sayac_wrapper['count']} üstün kaliteli sayfa indekslendi.")

# 🚀 [YENİ OTOMASYON MOTORU]: Zedin'in derinlemesine tarayacağı yüksek otoriteli kaynaklar
TOHUM_LISTESI = [
    "https://www.meb.gov.tr", "https://www.yok.gov.tr", "https://www.osym.gov.tr",
    "https://www.eba.gov.tr", "https://www.tubitak.gov.tr", "https://dergipark.org.tr",
    "https://www.itu.edu.tr", "https://www.odtu.edu.tr", "https://www.bogazici.edu.tr",
    "https://www.istanbul.edu.tr", "https://www.ankara.edu.tr", "https://www.hacettepe.edu.tr",
    "https://www.aa.com.tr", "https://www.trthaber.com", "https://teyit.org",
    "https://www.dogrulukpayi.com", "https://www.malumatfurus.org", "https://www.dogrula.org"
]

def zedin_otomatik_besleme():
    print("\n[ZEDIN OTOMASYON] Canlı paralel indeksleme motoru arka planda uyandırıldı...")
    import random
    karisik_tohumlar = list(TOHUM_LISTESI)
    random.shuffle(karisik_tohumlar)

    for ana_site in karisik_tohumlar:
        print(f"[ZEDIN OTOMASYON] Keşfediliyor: {ana_site}")
        try:
            # 🚀 Sınırlar genişletildi: Her ana kök site için limit 1500 sayfaya çıkarıldı
            link_ayıkla_ve_tarla(ana_site, max_sayfa=1500, eszamanli_isci=12)
            time.sleep(5)
        except Exception as e:
            print(f"[ZEDIN OTOMASYON HATA] {ana_site} atlandı: {e}")
            continue

if __name__ == "__main__":
    veritabani_olustur()
    url = input("Taranacak başlangıç adresini girin: ")
    try:
        # 🚀 [LİMİT GENİŞLETİLDİ]: 1000 sınırı kaldırılarak büyük çaplı veri çekimi sağlandı.
        limit = int(input("Kaç sayfa taransın? (Örn: 5000): "))
    except:
        limit = 500
        
    print(f"Zedin Örümceği paralel otomasyon modunda başlatılıyor! Hedef: {limit} sayfa...")
    link_ayıkla_ve_tarla(url, max_sayfa=limit, eszamanli_isci=10)

