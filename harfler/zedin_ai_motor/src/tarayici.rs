use reqwest::Client;
use scraper::{Html, Selector};
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::time::Duration;
use serde_json::json;

// Web sayfasından başlık ve temiz metin özetini söken fonksiyon
fn sayfa_icerik_ayıkla(html_icerik: &str) -> Option<(String, String)> {
    let fragment = Html::parse_document(html_icerik);
    
    // 1. Başlığı Seç
    let baslik_selector = Selector::parse("title").unwrap();
    let baslik = fragment
        .select(&baslik_selector)
        .next()
        .map(|e| e.text().collect::<String>().trim().to_string())
        .unwrap_or_else(|| "".to_string());

    // 2. Sayfa Gövdesindeki Yazıları Seç
    let govde_selector = Selector::parse("body").unwrap();
    let ham_metin = fragment
        .select(&govde_selector)
        .next()?
        .text()
        .collect::<String>();

    // Boşlukları temizle ve tek satıra indir
    let temiz_metin: String = ham_metin.split_whitespace().collect::<Vec<&str>>().join(" ");
    
    if temiz_metin.len() < 150 { return None; } // İçeriksiz siteleri pass geç

    Some((baslik, temiz_metin))
}

// Belirtilen harf grubunun listesini internetten tarayıp indeksleyen ana fonksiyon
pub async fn harf_grubunu_tara(client: Client, harf: char) -> std::io::Result<()> {
    let kaynak_adi = format!("{}_temiz.txt", harf);
    let hedef_adi = format!("indeks_{}.json", harf);

    if !std::path::Path::new(&kaynak_adi).exists() {
        return Ok(());
    }

    println!("\n🌐 [{}] GRUBU İÇİN CANLI WEB TARAMASI BAŞLADI 🌐", harf.to_uppercase());

    let dosya = File::open(&kaynak_adi)?;
    let okuyucu = BufReader::new(dosya);

    // JSONLines formatında dosya sonuna ekleme (Append) modunda açıyoruz (Termux dostu)
    let mut yazar = OpenOptions::new()
        .create(true)
        .append(true)
        .open(&hedef_adi)?;

    for satir in okuyucu.lines() {
        let domain = satir?.trim().to_string();
        if domain.is_empty() { continue; }

        let url = format!("https://www.{}", domain);
        println!("[*] İsteniyor: {}", url);

        // Sunucuyu yormadan ve engellenmeden 4 saniyelik zaman aşımı ile bağlan
        match client.get(&url).timeout(Duration::from_secs(4)).send().await {
            Ok(response) => {
                // Sadece HTML sayfalarını indeksle (Resim, PDF vs. ayıkla)
                if let Some(content_type) = response.headers().get("content-type") {
                    if !content_type.to_str().unwrap_or("").contains("text/html") {
                        continue;
                    }
                }

                if let Ok(html) = response.text().await {
                    if let Some((baslik, metin)) = sayfa_icerik_ayıkla(&html) {
                        
                        // Gerçek Yapay Zeka Arama İndeksi Verisi (Gerçek Başlık ve Gerçek İçerik)
                        let json_kayit = json!({
                            "url": url,
                            "title": baslik.chars().take(120).collect::<String>(),
                            "snippet": metin.chars().take(400).collect::<String>() // İlk 400 karakter özet
                        });

                        if writeln!(yazar, "{}", json_kayit.to_string()).is_ok() {
                            println!("    ✅ BAŞARILI -> İndekslendi: {}", json_kayit["title"]);
                        }
                    }
                }
            }
            Err(_) => {
                println!("    ❌ BAĞLANTI HATASI -> {} (Atlandı)", domain);
            }
        }
    }

    Ok(())
}

