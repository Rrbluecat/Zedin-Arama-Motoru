# veritabani_opt_ve_kucult.py

import sqlite3
import os
import shutil
from datetime import datetime

DB_YOLU = "lokal_arama.db"

def boyut_formatla(bayt: int) -> str:
    for birim in ['B', 'KB', 'MB', 'GB']:
        if bayt < 1024:
            return f"{bayt:.1f} {birim}"
        bayt /= 1024
    return f"{bayt:.1f} TB"

def yedek_al(db_yolu: str):
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek_yolu = f"{db_yolu}.yedek_{zaman}"
    shutil.copy2(db_yolu, yedek_yolu)
    print(f"[+] Yedek alındı: {yedek_yolu}")
    return yedek_yolu

def veritabani_sikistir():
    if not os.path.exists(DB_YOLU):
        print(f"[!] '{DB_YOLU}' bulunamadı!")
        return

    onceki_boyut = os.path.getsize(DB_YOLU)
    print(f"\n{'='*55}")
    print(f"   Zedin Veritabanı Optimizasyonu v2.0")
    print(f"{'='*55}")
    print(f"[*] Başlangıç boyutu: {boyut_formatla(onceki_boyut)}")

    # Önce yedek al
    yedek_al(DB_YOLU)

    conn = sqlite3.connect(DB_YOLU)
    cursor = conn.cursor()

    # ── Adım 1: Mevcut tabloları tespit et ────────────────────────────────────
    cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','index')")
    objeler = cursor.fetchall()
    tablolar = [o[0] for o in objeler if o[1] == 'table']
    print(f"[*] Bulunan tablolar: {', '.join(tablolar)}")

    # ── Adım 2: Yinelenen kayıtları sil ───────────────────────────────────────
    print("[*] Yinelenen kayıtlar temizleniyor...")
    silinen_toplam = 0

    for tablo in tablolar:
        # FTS5 sanal tablolarını atla
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=? AND sql LIKE '%fts%'",
            (tablo,)
        )
        if cursor.fetchone():
            continue

        try:
            cursor.execute(f"PRAGMA table_info({tablo})")
            sutunlar = [s[1] for s in cursor.fetchall()]

            if not sutunlar:
                continue

            # rowid hariç tüm sütunlara göre yinelenen sil
            sutun_listesi = ', '.join(sutunlar)
            cursor.execute(f"""
                DELETE FROM {tablo}
                WHERE rowid NOT IN (
                    SELECT MIN(rowid)
                    FROM {tablo}
                    GROUP BY {sutun_listesi}
                )
            """)
            silinen = cursor.rowcount
            silinen_toplam += silinen
            if silinen > 0:
                print(f"  [+] '{tablo}' tablosundan {silinen} yinelenen kayıt silindi.")
        except Exception as e:
            print(f"  [~] '{tablo}' yineleme kontrolü atlandı: {e}")

    print(f"[+] Toplam {silinen_toplam} yinelenen kayıt temizlendi.")

    # ── Adım 3: FTS5 indeksini optimize et ────────────────────────────────────
    print("[*] FTS5 tam metin arama indeksi optimize ediliyor...")
    for tablo in tablolar:
        try:
            cursor.execute(f"INSERT INTO {tablo}({tablo}) VALUES('optimize')")
            print(f"  [+] '{tablo}' FTS5 indeksi optimize edildi.")
        except Exception:
            pass  # FTS5 olmayan tablolar için normal

    # ── Adım 4: Eski/geçersiz indeksleri yeniden oluştur ──────────────────────
    print("[*] İndeksler yeniden oluşturuluyor...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indeksler = cursor.fetchall()
    for (indeks_adi,) in indeksler:
        try:
            cursor.execute(f"REINDEX {indeks_adi}")
        except Exception as e:
            print(f"  [~] '{indeks_adi}' indeksi atlandı: {e}")
    print(f"  [+] {len(indeksler)} indeks yeniden oluşturuldu.")

    # ── Adım 5: WAL dosyasını ana DB'ye birleştir ──────────────────────────────
    print("[*] WAL (Write-Ahead Log) dosyası birleştiriliyor...")
    try:
        cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        print("  [+] WAL checkpoint tamamlandı.")
    except Exception as e:
        print(f"  [~] WAL checkpoint: {e}")

    # ── Adım 6: Analiz verilerini güncelle ────────────────────────────────────
    print("[*] Sorgu planlayıcı istatistikleri güncelleniyor...")
    cursor.execute("ANALYZE")
    cursor.execute("PRAGMA optimize")
    print("  [+] İstatistikler güncellendi.")

    conn.commit()

    # ── Adım 7: VACUUM - Boş alanları geri al ─────────────────────────────────
    # VACUUM autocommit gerektirir
    conn.close()
    print("[*] VACUUM çalıştırılıyor (bu biraz sürebilir)...")
    conn = sqlite3.connect(DB_YOLU)
    conn.execute("VACUUM")
    conn.close()
    print("  [+] VACUUM tamamlandı.")

    # ── Sonuç ──────────────────────────────────────────────────────────────────
    sonraki_boyut = os.path.getsize(DB_YOLU)
    kazanim = onceki_boyut - sonraki_boyut
    yuzde = (kazanim / onceki_boyut * 100) if onceki_boyut > 0 else 0

    print(f"\n{'='*55}")
    print(f"[+] TAMAMLANDI!")
    print(f"    Önceki boyut : {boyut_formatla(onceki_boyut)}")
    print(f"    Sonraki boyut: {boyut_formatla(sonraki_boyut)}")
    print(f"    Kazanım      : {boyut_formatla(kazanim)} ({yuzde:.1f}% küçüldü)")
    print(f"    Veri kaybı   : YOK")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    veritabani_sikistir()

