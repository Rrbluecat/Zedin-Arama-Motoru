import os
import subprocess
# Daha önce yazdığımız aktarıcı fonksiyonunu çağırıyoruz
from indeks_aktarici import verileri_shardlara_bol

def sunucuya_ve_githuba_bagla():
    print("\n[ZEDİN KÖPRÜ] 1. Adım: SQLite verileri Rust JSON şardlarına dönüştürülüyor...")
    # 1. SQLite'taki verileri harfler/zedin_ai_motor klasörüne JSON olarak dağıt
    verileri_shardlara_bol()
    
    print("\n[ZEDİN KÖPRÜ] 2. Adım: Güncellenen indeksler GitHub sunucusuna gönderiliyor...")
    
    # 2. Git komutlarını sırayla güvenli bir şekilde çalıştır
    try:
        # Değişiklikleri ekle
        subprocess.run(["git", "add", "harfler/"], check=True)
        
        # Commit at (GPG imzalama kapalı olduğu için hata vermez)
        commit_mesaji = "Zedin Sunucu Guncellemesi: Yeni indeksler yuklendi"
        subprocess.run(["git", "commit", "-m", commit_mesaji], check=True)
        
        # GitHub'a pushla
        print("[*] GitHub'a pushlanıyor (Token ile giriş yaptıysan otomatik yüklenir)...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("\n[✓ BAŞARILI] Tüm indeksler hem Rust motoruna ayrıştırıldı hem de GitHub sunucuna uçuruldu!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n[X] Git işlemleri sırasında bir hata oluştu: {e}")
    except Exception as ex:
        print(f"\n[X] Beklenmedik hata: {ex}")

if __name__ == "__main__":
    sunucuya_ve_githuba_bagla()

