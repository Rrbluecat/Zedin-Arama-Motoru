import json
import os
import requests
import time
import urllib.parse
from bs4 import BeautifulSoup
from optimizasyon import ZedinOptimizer

session = requests.Session()
session.headers.update({'User-Agent': 'ZedinBot/2.0'})
optimizer = ZedinOptimizer(benzerlik_esigi=5)

def veritabani_olustur():
    """Veritabanı ve tabloyu oluşturur, yoksa yaratır."""
    # SQLite yerine JSON deposunu kontrol eder ve yoksa oluşturur
    if not os.path.exists('arama_indeksi.json'):
        with open('arama_indeksi.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    print("[DB] Veritabanı hazır.")

def link_ayıkla_ve_tarla(baslangic_url, max_sayfa=1000):
    tarandilar = set()
    kuyruk = [baslangic_url]
    sayac = 0
    baslangic_domain = urllib.parse.urlsplit(baslangic_url).netloc

    # SQL bağlantısı yerine mevcut JSON verilerini hafızaya yükleme
    sıkıstırılmıs_indeks = []
    mevcut_urller = set()
    if os.path.exists('arama_indeksi.json'):
        try:
            with open('arama_indeksi.json', 'r', encoding='utf-8') as f:
                sıkıstırılmıs_indeks = json.load(f)
                for veri in sıkıstırılmıs_indeks:
                    if len(veri) > 0:
                        mevcut_urller.add(veri[0])
        except:
            sıkıstırılmıs_indeks = []

    try:
        while kuyruk and sayac < max_sayfa:
            url = kuyruk.pop(0)
            url = optimizer.link_temizle(url)

            if url in tarandilar:
                continue

            try:
                response = session.get(url, timeout=5)
                tarandilar.add(url)

                if response.status_code != 200 or 'text/html' not in response.headers.get('Content-Type', ''):
                    continue

                soup = BeautifulSoup(response.text, 'lxml')

                for element in soup(["script", "style", "nav", "footer", "header", "aside", "svg"]):
                    element.decompose()

                icerik = ' '.join(soup.get_text().split())

                if len(icerik) < 300:
                    print(f"[ELEDİ] {url} - İçerik yetersiz")
                    continue

                if optimizer.kopya_icerik_mi(icerik, url=url):
                    print(f"[KOPYA ENGELLENDİ] {url}")
                    continue

                baslik = soup.title.string.strip() if soup.title else url

                try:
                    # UNIQUE NOT NULL kısıtlaması simülasyonu
                    if url in mevcut_urller:
                        raise Exception("IntegrityError")

                    # İstemci tarafındaki (arayüz) JS motorunun tam performans okuyabileceği formata sıkıştırarak ekliyoruz
                    sıkıstırılmıs_indeks.append([url, baslik[:60], icerik[:80]])
                    mevcut_urller.add(url)

                    # SQL Commit simülasyonu: JSON dosyasını diske kilitler
                    with open('arama_indeksi.json', 'w', encoding='utf-8') as f:
                        json.dump(sıkıstırılmıs_indeks, f, ensure_ascii=False, separators=(',', ':'))

                    sayac += 1
                    print(f"[{sayac}] İndekslendi: {baslik}")
                except:
                    print(f"[ATLA] Zaten var: {url}")

                for a_etiketi in soup.find_all('a', href=True):
                    link = a_etiketi['href']
                    tam_link = urllib.parse.urljoin(url, link)
                    tam_link = urllib.parse.urlsplit(tam_link)._replace(fragment="").geturl()
                    tam_link = optimizer.link_temizle(tam_link)
                    mevcut_domain = urllib.parse.urlsplit(tam_link).netloc

                    if (tam_link.startswith('http') and
                        mevcut_domain == baslangic_domain and
                        tam_link not in tarandilar and
                        tam_link not in kuyruk):
                        kuyruk.append(tam_link)

                time.sleep(0.1)

            except Exception as e:
                print(f"Hata ({url}): {e}")
    finally:
        print(f"\n[BİTTİ] Toplam {sayac} sayfa indekslendi.")

if __name__ == "__main__":
    veritabani_olustur()
    url = input("Taranacak başlangıç adresini girin: ")
    try:
        limit = int(input("Kaç sayfa taransın? (Maks 1000): "))
        if limit > 1000: limit = 1000
    except:
        limit = 100

    print(f"Zedin Örümceği başlatılıyor! Hedef: {limit} sayfa...")
    link_ayıkla_ve_tarla(url, max_sayfa=limit)

