import sqlite3

def veritabani_kur():
    conn = sqlite3.connect('lokal_arama.db')
    cursor = conn.cursor()

    # HIZ SİHRİ: WAL modunu açıyoruz ve senkronizasyonu gevşetiyoruz
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")

    # YENİ: DROP TABLE kaldırıldı! Tablo yoksa oluşturulacak, varsa eskilere dokunulmayacak.
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS sayfalar USING fts5(
            url,
            baslik,
            icerik,
            tokenize='porter unicode61'
        )
    ''')
    conn.commit()
    conn.close()
    print("Zedin FTS5 (WAL Modu) başarıyla kontrol edildi/kuruldu! Eski veriler güvende.")

if __name__ == "__main__":
    veritabani_kur()

