mod tarayici;
use reqwest::Client;
use std::time::Instant;

#[tokio::main]
async fn main() {
    let baslangic = Instant::now();

    println!("==================================================");
    println!(" 🪐 ZEDIN MULTI-TASK ASENKRON WEB CRAWLER");
    println!("==================================================");

    // Gerçek bir tarayıcı (Browser) gibi davranması için HTTP Header ayarları
    let client = Client::builder()
        .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) ZedinBot/5.0")
        .pool_max_idle_per_host(3)
        .build()
        .unwrap();

    // Alfabedeki tüm harf temiz listelerini sırayla gerçek web taramasına al
    for harf in "abcdefghijklmnopqrstuvwxyz".chars() {
        let istemci_kopyasi = client.clone();
        if let Err(e) = tarayici::harf_grubunu_tara(istemci_kopyasi, harf).await {
            println!("[!] {} grubu taranırken kritik hata: {}", harf, e);
        }
    }

    println!("==================================================");
    println!("[+] Canlı indeksleme tamamlandı. Kaliteli YZ veri havuzu hazır!");
    println!("[+] Toplam harcanan süre: {:?}", baslangic.elapsed());
    println!("==================================================");
}

