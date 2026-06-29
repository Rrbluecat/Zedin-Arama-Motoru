import sqlite3
import json
import os
from collections import defaultdict

DB_NAME = 'zedin_lokal.db'
HEDEF_KLASOR = 'harfler/zedin_ai_motor'

def verileri_shardlara_bol():
    """SQLite veritabanındaki tüm verileri harflerine göre ayırıp Rust indeks JSON'larına yazar."""
    if not os.path.exists(DB_NAME):
        print(f"[HATA] {DB_NAME} bulunamadı! Önce tarayıcıyı çalıştırıp biraz veri toplayın.")
        return

    print("[Aktarıcı] SQLite veritabanına bağlanılıyor...")

    # 1. SQLite'tan tüm verileri tek seferde çek (Hızlı okuma)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT url, baslik, icerik, harf FROM indeks")
    satirlar = cursor.fetchall()
    conn.close()

    if not satirlar:
        print("[UYARI] Veritabanında hiç kayıt yok. Aktarım iptal edildi.")
        return

    print(f"[Aktarıcı] Toplam {len(satirlar)} kayıt hafızaya alındı. Ayrıştırma başlıyor...")

    # 2. Verileri harf sütununa göre RAM üzerinde grupla
    shard_gruplari = defaultdict(list)
    for url, baslik, icerik, harf in satirlar:
        # Eğer harf atanmamışsa güvenli bir varsayılan kategoriye at
        if not harf or harf.strip() == "":
            harf = "numara_sembol"

        # Rust motorunun beklediği sıkıştırılmış liste formatı: [url, baslik, icerik]
        sayfa_verisi = [url, baslik, icerik]
        shard_gruplari[harf.lower()].append(sayfa_verisi)

    # Hedef klasörün var olduğundan emin ol
    os.makedirs(HEDEF_KLASOR, exist_ok=True)

    print("[Aktarıcı] JSON dosyaları güncelleniyor...")

    # 3. Her harf grubunu kendi JSON dosyasına temizce yaz
    # SQLite ana kaynak olduğu için üzerine yazmak (overwrite) en temizidir, mükerrerliği sıfırlar.
    for harf, yeni_veriler in shard_gruplari.items():
        dosya_adi = f"indeks_{harf}.json"
        dosya_yolu = os.path.join(HEDEF_KLASOR, dosya_adi)

        try:
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                # separators kullanarak boşlukları siliyoruz, dosya boyutu %30 küçülüyor
                json.dump(yeni_veriler, f, ensure_ascii=False, separators=(',', ':'))
            print(f" 📝 {dosya_adi} güncellendi -> {len(yeni_veriler)} sayfa.")
        except Exception as e:
            print(f" ❌ {dosya_adi} yazılırken hata oluştu: {e}")

    print("\n[BAŞARILI] Tüm SQLite verileri Rust motorunun şafelerine (JSON) aktarıldı!")

if __name__ == "__main__":
    verileri_shardlara_bol()

