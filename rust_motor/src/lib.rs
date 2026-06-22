use pyo3::prelude::*;
use pyo3::types::PySet;
use rayon::prelude::*;
use reqwest::blocking::Client;
use scraper::{Html, Selector};
use std::collections::HashSet;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use rand::seq::SliceRandom;
use url::Url;

const USER_AGENTS: &[&str] = &[
    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
];

const TR_UZANTILARI: &[&str] = &[
    "com.tr", "net.tr", "org.tr", "edu.tr", "gov.tr",
    "mil.tr", "pol.tr", "bel.tr", "av.tr",  "dr.tr",
    "web.tr", "info.tr","gen.tr", "bbs.tr", "name.tr",
    "tel.tr", "tv.tr",  "k12.tr", "fin.tr", "vet.tr",
];

fn client_olustur() -> Client {
    let mut rng = rand::thread_rng();
    let ua = USER_AGENTS.choose(&mut rng).unwrap_or(&USER_AGENTS[0]);
    Client::builder()
        .user_agent(*ua)
        .timeout(Duration::from_secs(30))
        .connect_timeout(Duration::from_secs(15))
        .gzip(true)
        .brotli(true)
        .build()
        .unwrap_or_default()
}

fn domain_temizle(ham: &str) -> Option<String> {
    let ham = if ham.starts_with("http") {
        ham.to_string()
    } else {
        format!("https://{}", ham)
    };
    let parsed = Url::parse(&ham).ok()?;
    let host = parsed.host_str()?.to_lowercase();
    let host = host.trim_start_matches("www.");
    let host = host.split(':').next()?;
    if host.ends_with(".tr") && !host.contains(' ') && host.len() > 4 {
        Some(host.to_string())
    } else {
        None
    }
}

fn crtsh_tara(uzanti: &str) -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();
    let mut offset = 0usize;
    let limit = 10000usize;

    loop {
        let url = format!(
            "https://crt.sh/?q=%.{}&output=json&limit={}&offset={}",
            uzanti, limit, offset
        );

        let mut deneme = 0u32;
        let yanit = loop {
            deneme += 1;
            match client.get(&url).send() {
                Ok(r) if r.status().as_u16() == 429 => {
                    let bekleme = deneme * 15;
                    println!("[crt.sh] .{} rate limit, {}s bekleniyor...", uzanti, bekleme);
                    std::thread::sleep(Duration::from_secs(bekleme as u64));
                    if deneme >= 5 { break None; }
                }
                Ok(r) if r.status().as_u16() == 502 || r.status().as_u16() == 503 => {
                    println!("[crt.sh] .{} sunucu hatası, 10s bekleniyor...", uzanti);
                    std::thread::sleep(Duration::from_secs(10));
                    if deneme >= 3 { break None; }
                }
                Ok(r) if r.status().is_success() => break Some(r),
                Ok(r) => {
                    println!("[crt.sh] .{} HTTP {}", uzanti, r.status());
                    break None;
                }
                Err(e) => {
                    println!("[crt.sh] .{} hata (deneme {}): {}", uzanti, deneme, e);
                    std::thread::sleep(Duration::from_secs(deneme as u64 * 5));
                    if deneme >= 4 { break None; }
                }
            }
        };

        match yanit {
            None => break,
            Some(resp) => {
                let metin = match resp.text() { Ok(t) => t, Err(_) => break };
                if metin.trim().is_empty() || metin == "[]" { break }
                let veri: Vec<serde_json::Value> = match serde_json::from_str(&metin) {
                    Ok(v) => v, Err(_) => break
                };
                if veri.is_empty() { break }
                let onceki = domainler.len();
                for kayit in &veri {
                    if let Some(isim) = kayit["name_value"].as_str() {
                        for satir in isim.split('\n') {
                            let temiz = satir.trim().trim_start_matches("*.");
                            if temiz.ends_with(".tr") && !temiz.contains(' ') {
                                domainler.insert(temiz.to_lowercase());
                            }
                        }
                    }
                }
                println!("[crt.sh] .{} offset={} → {} yeni (toplam {})",
                    uzanti, offset, domainler.len() - onceki, domainler.len());
                if veri.len() < limit { break }
                offset += limit;
                std::thread::sleep(Duration::from_millis(1500));
            }
        }
    }
    domainler
}

fn wayback_tara(uzanti: &str) -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();
    let mut sayfa = 0u32;

    loop {
        let url = format!(
            "https://web.archive.org/cdx/search/cdx?url=*.{}/*&output=json&fl=original&limit=10000&collapse=urlkey&filter=statuscode:200&page={}",
            uzanti, sayfa
        );
        let mut deneme = 0u32;
        let yanit = loop {
            deneme += 1;
            match client.get(&url).send() {
                Ok(r) if r.status().is_success() => break Some(r),
                Ok(r) if r.status().as_u16() == 429 => {
                    std::thread::sleep(Duration::from_secs(deneme as u64 * 10));
                    if deneme >= 3 { break None; }
                }
                Err(e) => {
                    println!("[Wayback] .{} hata (deneme {}): {}", uzanti, deneme, e);
                    std::thread::sleep(Duration::from_secs(5));
                    if deneme >= 3 { break None; }
                }
                _ => break None,
            }
        };

        match yanit {
            None => break,
            Some(resp) => {
                let metin = match resp.text() { Ok(t) => t, Err(_) => break };
                let veri: Vec<Vec<String>> = match serde_json::from_str(&metin) {
                    Ok(v) => v, Err(_) => break
                };
                if veri.len() <= 1 { break }
                for satir in veri.iter().skip(1) {
                    if let Some(u) = satir.first() {
                        if let Some(d) = domain_temizle(u) {
                            domainler.insert(d);
                        }
                    }
                }
                println!("[Wayback] .{} sayfa={} → {} domain", uzanti, sayfa, domainler.len());
                if veri.len() < 10001 { break }
                sayfa += 1;
                std::thread::sleep(Duration::from_millis(800));
            }
        }
    }
    domainler
}

fn common_crawl_tara(uzanti: &str) -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();
    let indeksler = [
        "CC-MAIN-2024-10", "CC-MAIN-2023-50",
        "CC-MAIN-2023-40", "CC-MAIN-2022-49",
    ];

    for indeks in &indeksler {
        let mut sayfa = 0u32;
        loop {
            let url = format!(
                "https://index.commoncrawl.org/{}-index?url=*.{}/*&output=json&fl=url&limit=1000&page={}",
                indeks, uzanti, sayfa
            );
            match client.get(&url).send() {
                Ok(resp) if resp.status().is_success() => {
                    let metin = match resp.text() { Ok(t) => t, Err(_) => break };
                    if metin.trim().is_empty() { break }
                    let mut yeni = 0;
                    for satir in metin.lines() {
                        if let Ok(veri) = serde_json::from_str::<serde_json::Value>(satir) {
                            if let Some(u) = veri["url"].as_str() {
                                if let Some(d) = domain_temizle(u) {
                                    if domainler.insert(d) { yeni += 1; }
                                }
                            }
                        }
                    }
                    if yeni == 0 { break }
                    sayfa += 1;
                    std::thread::sleep(Duration::from_millis(300));
                }
                _ => break,
            }
        }
    }
    println!("[CommonCrawl] .{} → {} domain", uzanti, domainler.len());
    domainler
}

fn hackertarget_tara(uzanti: &str) -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();
    let url = format!("https://api.hackertarget.com/hostsearch/?q={}", uzanti);
    if let Ok(resp) = client.get(&url).send() {
        if let Ok(metin) = resp.text() {
            for satir in metin.lines() {
                let p: Vec<&str> = satir.split(',').collect();
                if let Some(d) = p.first() {
                    if d.ends_with(".tr") {
                        domainler.insert(d.trim().to_lowercase());
                    }
                }
            }
        }
    }
    println!("[HackerTarget] .{} → {} domain", uzanti, domainler.len());
    domainler
}

fn rapiddns_tara(uzanti: &str) -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();
    let url = format!("https://rapiddns.io/s/{}?full=1&down=1", uzanti);
    if let Ok(resp) = client.get(&url).send() {
        if let Ok(metin) = resp.text() {
            let belge = Html::parse_document(&metin);
            if let Ok(secici) = Selector::parse("td") {
                for td in belge.select(&secici) {
                    let t = td.text().collect::<String>();
                    let t = t.trim().to_string();
                    if t.ends_with(".tr") {
                        if let Some(d) = domain_temizle(&format!("https://{}", t)) {
                            domainler.insert(d);
                        }
                    }
                }
            }
        }
    }
    println!("[RapidDNS] .{} → {} domain", uzanti, domainler.len());
    domainler
}

fn urlscan_tara(uzanti: &str) -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();
    let url = format!(
        "https://urlscan.io/api/v1/search/?q=domain%3A{}&size=10000",
        uzanti
    );
    if let Ok(resp) = client.get(&url).send() {
        if let Ok(metin) = resp.text() {
            if let Ok(veri) = serde_json::from_str::<serde_json::Value>(&metin) {
                if let Some(sonuclar) = veri["results"].as_array() {
                    for s in sonuclar {
                        if let Some(d) = s["page"]["domain"].as_str() {
                            if d.ends_with(".tr") {
                                domainler.insert(d.to_lowercase());
                            }
                        }
                    }
                }
            }
        }
    }
    println!("[URLScan] .{} → {} domain", uzanti, domainler.len());
    domainler
}

fn nictr_tara() -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();
    let mut cursor = 0usize;

    loop {
        let url = format!("https://rdap.nic.tr/domains?cursor={}&count=500", cursor);
        match client.get(&url).send() {
            Ok(resp) if resp.status().is_success() => {
                if let Ok(veri) = resp.json::<serde_json::Value>() {
                    let sonuclar = match veri["domainSearchResults"].as_array() {
                        Some(s) => s.clone(),
                        None => break,
                    };
                    if sonuclar.is_empty() { break }
                    for kayit in &sonuclar {
                        if let Some(isim) = kayit["ldhName"].as_str() {
                            let isim = isim.to_lowercase();
                            if isim.ends_with(".tr") {
                                domainler.insert(isim);
                            }
                        }
                    }
                    println!("[NIC.TR] cursor={} → {} domain", cursor, domainler.len());
                    cursor += 500;
                    std::thread::sleep(Duration::from_secs(1));
                } else { break }
            }
            _ => break,
        }
    }
    domainler
}

#[pyfunction]
fn tum_domainleri_topla(py: Python) -> PyResult<Py<PySet>> {
    println!("[Rust] Tarama başlatıldı...");
    let sonuclar: Arc<Mutex<HashSet<String>>> = Arc::new(Mutex::new(HashSet::new()));

    // NIC.TR tek seferlik
    let nictr = nictr_tara();
    println!("[NIC.TR] {} domain", nictr.len());
    sonuclar.lock().unwrap().extend(nictr);

    // crt.sh SIRALI (rate limit yememek için)
    println!("[*] crt.sh sıralı taranıyor...");
    for uzanti in TR_UZANTILARI {
        let sonuc = crtsh_tara(uzanti);
        println!("[crt.sh] .{} → {} domain", uzanti, sonuc.len());
        sonuclar.lock().unwrap().extend(sonuc);
        std::thread::sleep(Duration::from_secs(3));
    }

    // Diğer kaynaklar PARALEL
    println!("[*] Diğer kaynaklar paralel taranıyor...");
    TR_UZANTILARI.par_iter().for_each(|uzanti| {
        let mut yerel = HashSet::new();
        yerel.extend(wayback_tara(uzanti));
        yerel.extend(common_crawl_tara(uzanti));
        yerel.extend(hackertarget_tara(uzanti));
        yerel.extend(rapiddns_tara(uzanti));
        yerel.extend(urlscan_tara(uzanti));

        let mut kilit = sonuclar.lock().unwrap();
        let onceki = kilit.len();
        kilit.extend(yerel);
        println!("[Rust] .{} bitti → +{} yeni (Toplam: {})",
            uzanti, kilit.len() - onceki, kilit.len());
    });

    let kilit = sonuclar.lock().unwrap();
    let py_set = PySet::new_bound(py, kilit.iter())?;
    Ok(py_set.into())
}

#[pyfunction]
fn crtsh_hizli_tara(py: Python, uzanti: String) -> PyResult<Py<PySet>> {
    let domainler = crtsh_tara(&uzanti);
    let py_set = PySet::new_bound(py, domainler.iter())?;
    Ok(py_set.into())
}


fn tr_linkleri_cek(url: &str) -> HashSet<String> {
    let mut domainler = HashSet::new();
    let client = client_olustur();

    match client.get(url).send() {
        Ok(resp) if resp.status().is_success() => {
            if let Ok(metin) = resp.text() {
                let belge = Html::parse_document(&metin);
                if let Ok(secici) = Selector::parse("a[href]") {
                    for a in belge.select(&secici) {
                        if let Some(href) = a.value().attr("href") {
                            if let Some(d) = domain_temizle(href) {
                                domainler.insert(d);
                            }
                        }
                    }
                }
            }
        }
        _ => {}
    }
    domainler
}

#[pyfunction]
fn domain_listesini_tara(py: Python, dosya_yolu: String) -> PyResult<Py<PySet>> {
    use std::io::{BufRead, BufReader};
    use std::fs::File;

    println!("[Rust] Domain listesi okunuyor: {}", dosya_yolu);

    let dosya = File::open(&dosya_yolu)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;

    let satirlar: Vec<String> = BufReader::new(dosya)
        .lines()
        .filter_map(|l| l.ok())
        .filter(|l| l.starts_with("http") && l.contains(".tr"))
        .collect();

    println!("[Rust] {} domain taranacak", satirlar.len());

    let bulunan: Arc<Mutex<HashSet<String>>> = Arc::new(Mutex::new(HashSet::new()));
    let sayac: Arc<Mutex<usize>> = Arc::new(Mutex::new(0));

    satirlar.par_iter().for_each(|url| {
        let yeni = tr_linkleri_cek(url);
        let mut kilit = bulunan.lock().unwrap();
        let onceki = kilit.len();
        kilit.extend(yeni);
        let mut s = sayac.lock().unwrap();
        *s += 1;
        if kilit.len() > onceki {
            println!("[{}/{}] {} -> +{} yeni domain (Toplam: {})",
                s, satirlar.len(), url,
                kilit.len() - onceki,
                kilit.len());
        }
    });

    let kilit = bulunan.lock().unwrap();
    println!("[Rust] Tarama bitti! {} yeni domain bulundu", kilit.len());
    let py_set = PySet::new_bound(py, kilit.iter())?;
    Ok(py_set.into())
}


// ─── Türkçe Stop Words (anlamsız kelimeler) ──────────────────────────────────
const STOP_WORDS: &[&str] = &[
    "bir", "bu", "şu", "o", "ve", "ile", "de", "da", "ki", "mi",
    "mu", "mü", "mı", "için", "ama", "fakat", "lakin", "ya", "veya",
    "hem", "ne", "en", "çok", "az", "daha", "gibi", "kadar", "sonra",
    "önce", "üzere", "göre", "karşı", "rağmen", "beri", "itibaren",
    "the", "and", "or", "is", "in", "on", "at", "to", "of", "a",
];

// ─── Türkçe Ek Temizleyici (basit kök bulma) ─────────────────────────────────
fn kok_bul(kelime: &str) -> String {
    let ekler = [
        "ların", "lerin", "ların", "lerin", "ların",
        "ların", "nın", "nin", "nun", "nün",
        "dan", "den", "tan", "ten",
        "da", "de", "ta", "te",
        "ya", "ye", "na", "ne",
        "lar", "ler", "ın", "in", "un", "ün",
        "ım", "im", "um", "üm",
        "dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür",
        "cı", "ci", "cu", "cü", "çı", "çi", "çu", "çü",
        "lık", "lik", "luk", "lük",
        "sız", "siz", "suz", "süz",
        "sal", "sel", "al", "el",
        "an", "en", "ar", "er",
        "mak", "mek", "yor", "iyor",
        "li", "lı", "lu", "lü",
        "ki", "nci", "ıncı", "inci",
    ];

    let k = kelime.to_lowercase();
    for ek in &ekler {
        if k.ends_with(ek) && k.len() > ek.len() + 2 {
            return k[..k.len() - ek.len()].to_string();
        }
    }
    k
}

// ─── Alakalılık Skoru Hesapla ─────────────────────────────────────────────────
fn alakalilik_skoru(sorgu_kokleri: &[String], baslik: &str, icerik: &str) -> f64 {
    let baslik_lower = baslik.to_lowercase();
    let icerik_lower = icerik.to_lowercase();
    let mut skor = 0.0;

    for kok in sorgu_kokleri {
        if kok.len() < 2 { continue; }

        // Başlıkta tam eşleşme: 10 puan
        if baslik_lower.contains(kok.as_str()) {
            skor += 10.0;
        }
        // İçerikte tam eşleşme: 2 puan
        if icerik_lower.contains(kok.as_str()) {
            skor += 2.0;
        }
        // Başlıkta kısmi eşleşme (en az 3 harf): 5 puan
        if kok.len() >= 3 {
            let kismi: String = kok.chars().take(3).collect();
            if baslik_lower.contains(&kismi) {
                skor += 5.0;
            }
            if icerik_lower.contains(&kismi) {
                skor += 1.0;
            }
        }
    }

    // Başlıkta sorgunun tamamı varsa bonus
    let tam_sorgu = sorgu_kokleri.join(" ");
    if baslik_lower.contains(&tam_sorgu) {
        skor += 20.0;
    }

    skor
}

#[pyfunction]
fn sonuclari_sirala_ve_filtrele(
    py: Python,
    sorgu: String,
    sonuclar: Vec<(String, String, String)>, // (url, baslik, icerik)
    min_skor: f64,
) -> PyResult<PyObject> {
    // Stop word temizle, kökleri bul
    let sorgu_kokleri: Vec<String> = sorgu
        .to_lowercase()
        .split_whitespace()
        .filter(|k| !STOP_WORDS.contains(k) && k.len() > 1)
        .map(|k| kok_bul(k))
        .collect();

    if sorgu_kokleri.is_empty() {
        let liste = pyo3::types::PyList::empty_bound(py);
        return Ok(liste.into());
    }

    // Her sonucu skorla
    let mut skorlu: Vec<(f64, &(String, String, String))> = sonuclar
        .iter()
        .map(|s| {
            let skor = alakalilik_skoru(&sorgu_kokleri, &s.1, &s.2);
            (skor, s)
        })
        .filter(|(skor, _)| *skor >= min_skor)
        .collect();

    // Skora göre sırala (yüksekten düşüğe)
    skorlu.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));

    // Python listesi olarak döndür
    let liste = pyo3::types::PyList::empty_bound(py);
    for (skor, satir) in &skorlu {
        let tuple = pyo3::types::PyTuple::new_bound(
            py,
            &[
                satir.0.as_str(),
                satir.1.as_str(),
                satir.2.as_str(),
                &format!("{:.1}", skor),
            ],
        );
        liste.append(tuple)?;
    }

    Ok(liste.into())
}

#[pymodule]
fn zedin_domain(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(tum_domainleri_topla, m)?)?;
    m.add_function(wrap_pyfunction!(crtsh_hizli_tara, m)?)?;
    ;
    m.add_function(wrap_pyfunction!(domain_listesini_tara, m)?)?
    ;
    m.add_function(wrap_pyfunction!(sonuclari_sirala_ve_filtrele, m)?)?;
    Ok(())
}
