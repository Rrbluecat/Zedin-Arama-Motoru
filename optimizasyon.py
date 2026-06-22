import re
import hashlib
import urllib.parse

class ZedinOptimizer:
    def __init__(self, benzerlik_esigi=5):
        """
        benzerlik_esigi: Hamming mesafesi eşiği.
        - 3 veya altı = neredeyse birebir kopya
        - 5 = çok benzer (önerilen)
        - 10 = orta benzer (çok agresif, yanlış pozitif artar)
        """
        self.parmak_izleri = []
        self.benzerlik_esigi = benzerlik_esigi

    def _kelime_hash(self, kelime: str) -> int:
        """Bir kelimeyi 64-bit tam sayıya hash'ler."""
        return int(hashlib.md5(kelime.encode('utf-8')).hexdigest(), 16) & 0xFFFFFFFFFFFFFFFF

    def simhash_hesapla(self, metin: str):
        """Metnin SimHash parmak izini hesaplar."""
        kelimeler = re.findall(r'\w+', metin.lower())

        if len(kelimeler) < 20:
            return None

        vektor = [0] * 64

        for kelime in kelimeler:
            h = self._kelime_hash(kelime)
            for i in range(64):
                if (h >> i) & 1:
                    vektor[i] += 1
                else:
                    vektor[i] -= 1

        parmak_izi = 0
        for i in range(64):
            if vektor[i] > 0:
                parmak_izi |= (1 << i)

        return parmak_izi

    def _hamming_mesafesi(self, hash1: int, hash2: int) -> int:
        """İki hash arasındaki farklı bit sayısını döner."""
        return bin(hash1 ^ hash2).count('1')

    def kopya_icerik_mi(self, icerik: str, url: str = "") -> bool:
        """
        İçeriğin daha önce indekslenmiş bir sayfaya çok benzeyip
        benzemediğini SimHash ile kontrol eder.
        Kopya ise True, değilse False döner ve parmak izini kaydeder.
        """
        yeni_hash = self.simhash_hesapla(icerik)

        if yeni_hash is None:
            return False

        for kayitli_hash, kayitli_url in self.parmak_izleri:
            mesafe = self._hamming_mesafesi(yeni_hash, kayitli_hash)
            if mesafe <= self.benzerlik_esigi:
                print(f"    -> Benzer sayfa: {kayitli_url} (mesafe={mesafe})")
                return True

        self.parmak_izleri.append((yeni_hash, url))
        return False

    def link_temizle(self, url: str) -> str:
        """URL'den gereksiz parametreleri temizler."""
        gereksiz_parametreler = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
            'utm_content', 'fbclid', 'gclid', 'ref', 'source',
            'mc_cid', 'mc_eid', 'yclid', '_ga', 'lang', 'sort',
            'order', 'view', 'theme'
        }
        try:
            parsed = urllib.parse.urlsplit(url)
            parametreler = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            temiz_parametreler = {
                k: v for k, v in parametreler.items()
                if k.lower() not in gereksiz_parametreler
            }
            temiz_query = urllib.parse.urlencode(temiz_parametreler, doseq=True)
            return urllib.parse.urlunsplit((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                temiz_query,
                ''
            ))
        except:
            return url

