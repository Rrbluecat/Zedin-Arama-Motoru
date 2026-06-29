use std::collections::HashMap;

pub struct OfflineAIModel {
    gecis_matrisi: HashMap<(char, char), f64>,
    esik_degeri: f64,
}

impl OfflineAIModel {
    pub fn new() -> Self {
        let mut matris = HashMap::new();
        let egitilmis_veriler = vec![
            (('h', 'a'), 0.85), (('a', 'b'), 0.75), (('b', 'e'), 0.80), (('e', 'r'), 0.90),
            (('t', 'u'), 0.70), (('u', 'r'), 0.85), (('r', 'k'), 0.95),
        ];
        for (cift, olasilik) in egitilmis_veriler { matris.insert(cift, olasilik); }

        OfflineAIModel { gecis_matrisi: matris, esik_degeri: 0.25 }
    }

    pub fn analiz_et(&self, domain: &str) -> bool {
        let saf_isim = domain.replace("www.", "").split('.').next().unwrap_or("").to_lowercase();
        if saf_isim.len() < 3 { return false; }

        let mut toplam_skor = 0.0;
        let mut gecis_sayisi = 0;
        let karakterler: Vec<char> = saf_isim.chars().collect();

        for i in 0..karakterler.len() - 1 {
            let mevcut = karakterler[i];
            let sonraki = karakterler[i + 1];
            if "qwxz".contains(mevcut) && "qwxz".contains(sonraki) { return false; }
            let skor = self.gecis_matrisi.get(&(mevcut, sonraki)).unwrap_or(&0.05);
            toplam_skor += *skor;
            gecis_sayisi += 1;
        }

        if gecis_sayisi == 0 { return false; }
        (toplam_skor / gecis_sayisi as f64) >= self.esik_degeri
    }
}

