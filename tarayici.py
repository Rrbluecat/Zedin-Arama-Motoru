import sqlite3
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
    conn = sqlite3.connect('lokal_arama.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sayfalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            baslik TEXT,
            icerik TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Veritabanı hazır.")

def link_ayıkla_ve_tarla(baslangic_url, max_sayfa=1000):
    tarandilar = set()
    kuyruk = [baslangic_url]
    sayac = 0
    baslangic_domain = urllib.parse.urlsplit(baslangic_url).netloc

    conn = sqlite3.connect('lokal_arama.db')
    cursor = conn.cursor()

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
                    cursor.execute(
                        "INSERT INTO sayfalar (url, baslik, icerik) VALUES (?, ?, ?)",
                        (url, baslik, icerik)
                    )
                    conn.commit()
                    sayac += 1
                    print(f"[{sayac}] İndekslendi: {baslik}")
                except sqlite3.IntegrityError:
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
        conn.close()
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

