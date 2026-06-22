import json
import os
import re

def metin_temizle(metin):
    if not metin:
        return ""
    # Birden fazla boşluğu, satır başlarını tek bir boşluğa indirger
    metin = re.sub(r'\s+', ' ', metin)
    return metin.strip()

def indeks_uret():
    cikti_json = "arama_indeksi.json"

    if not os.path.exists(cikti_json):
        print(f"[!] Hata: Klasörde '{cikti_json}' bulunamadı. Lütfen önce crawler'ı çalıştırın.")
        return

    print("[*] Küresel JSON indeksine bağlanılıyor...")

    try:
        # SQLite tablosu yerine doğrudan mevcut JSON verilerini çekiyoruz ve optimize ediyoruz
        with open(cikti_json, "r", encoding="utf-8") as f:
            satirlar = json.load(f)

        toplam_kayit = len(satirlar)
        print(f"[*] Toplam {toplam_kayit} adet sayfa bulundu. Dönüştürme başlıyor...")

        sıkıstırılmıs_indeks = []

        for sayfa in satirlar:
            url = sayfa[0]
            baslik = sayfa[1]
            icerik = sayfa[2]

            # OPTİMİZASYON 1: İçerik kırpma sınırını 300'den 80'e düşürerek boyuttan %70 kar ediyoruz.
            kisa_icerik = metin_temizle(icerik)[:80]
            temiz_baslik = metin_temizle(baslik)[:60] # Başlığı da makul bir sınırda tutuyoruz

            # OPTİMİZASYON 2: "u", "b", "i" anahtarlarını silip düz diziye (Array) çeviriyoruz.
            # Format artık şu şekilde: [url, baslik, icerik]
            sayfa_objesi = [
                url,
                temiz_baslik if temiz_baslik else url,
                kisa_icerik
            ]
            sıkıstırılmıs_indeks.append(sayfa_objesi)

        print("[*] Ultra-sıkıştırılmış JSON dosyası diske yazılıyor...")
        with open(cikti_json, "w", encoding="utf-8") as f:
            # separators boşlukları silerek JSON dosya boyutunu en dip seviyeye çeker
            json.dump(sıkıstırılmıs_indeks, f, ensure_ascii=False, separators=(',', ':'))

        json_boyut = os.path.getsize(cikti_json) / (1024 * 1024)

        print("\n=== 🎉 ULTRA SIKIŞTIRMA BAŞARILI ===")
        print(f"📊 İşlenen Sayfa: {toplam_kayit}")
        print(f"💾 Orijinal DB Boyutu: Pas geçildi (Mimariden kaldırıldı)")
        print(f"⚡ Yeni JSON İndeks Boyutu: {json_boyut:.4f} MB")
        print(f"💡 Kaydedilen Dosya: {cikti_json}")

    except Exception as e:
        print(f"[!] Bir hata oluştu: {e}")

if __name__ == "__main__":
    indeks_uret()

