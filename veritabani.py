import sqlite3

def veritabani_kur():
    conn = sqlite3.connect('lokal_arama.db')
    cursor = conn.cursor()
    # Siteleri ve içeriklerini tutacak tablo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sayfalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            baslik TEXT,
            icerik TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    veritabani_kur()
    print("Lokal veritabanı başarıyla oluşturuldu!")

