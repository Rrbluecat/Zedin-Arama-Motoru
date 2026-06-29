import os
import requests

def tranco_turkiye_ayikla():
    print("=" * 60)
    print(" 🚀 POPÜLER 1 MİLYON DOMAİNDEN TÜRKİYE SİTELERİNİ ÇEKME MOTORU")
    print("=" * 60)
    print("[*] Tranco güncel küresel top 1 milyon listesi indiriliyor...")
    
    # Bilimsel araştırmalar için kullanılan reklam ve spam barındırmayan en temiz liste
    url = "https://tranco-list.eu/download/daily/1000000" 
    
    try:
        # Stream=True sayesinde tüm dosyayı belleğe yüklemez, internetten geldikçe satır satır okur
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            print("[!] Listeye erişilemedi! Tranco sunucularında anlık bir sorun olabilir.")
            return
            
        print("[+] Bağlantı başarılı. Türkiye odaklı domainler süzülüyor...")
        
        turkiye_domainleri = []
        
        # Popüler Türkçe kelime kökleri (Bunu istediğin gibi genişletebilirsin)
        turkce_anahtarlar = [
            "haber", "sozcu", "milliyet", "hurriyet", "turk", "turkiye", 
            "indir", "film", "izle", "oyun", "bilgi", "kitap", "ders", 
            "okul", "universite", "forum", "blog", "gazete", "pazar"
        ]
        
        for satir in response.iter_lines(decode_unicode=True):
            if not satir:
                continue
                
            # Tranco CSV formatı: "Sıra,domain.com" şeklindedir
            parcalar = satir.strip().split(',')
            if len(parcalar) < 2:
                continue
                
            domain = parcalar[1].lower()
            
            # 1. KRİTER: Doğrudan Türkiye tescilli .tr uzantılı siteler
            if domain.endswith(".tr"):
                turkiye_domainleri.append(domain)
                continue
                
            # 2. KRİTER: .com, .net, .org olup içinde popüler Türkçe ipuçları barındıranlar
            if any(kelime in domain for kelime in turkce_anahtarlar):
                turkiye_domainleri.append(domain)

        HEDEF_DOSYA = "domainler.txt"
        
        # Eğer daha önceden domainler.txt varsa silmez, altına ekleme (append) yapar
        mod = "a" if os.path.exists(HEDEF_DOSYA) else "w"
        
        # Tekrarları önlemek için set kullanıyoruz
        benzersiz_domainler = sorted(list(set(turkiye_domainleri)))
        
        with open(HEDEF_DOSYA, mod, encoding="utf-8") as f:
            for d in benzersiz_domainler:
                f.write(f"{d}\n")
                
        print(f"\n[+] İŞLEM TAMAMLANDI!")
        print(f"    1 Milyon site arasından çekilen kaliteli Türkiye sitesi: {len(benzersiz_domainler)}")
        print(f"    Siteler doğrudan '{HEDEF_DOSYA}' dosyasına enjekte edildi.")
        
    except Exception as e:
        print(f"[!] Bir hata oluştu: {e}")
        print("[!] Not: 'requests' kütüphanesi kurulu değilse 'pip install requests' yazmalısın.")

if __name__ == "__main__":
    tranco_turkiye_ayikla()

