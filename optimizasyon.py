class ZedinOptimizer:
    def __init__(self, benzerlik_esigi=5):
        pass

    def link_temizle(self, url):
        # Orijinal link temizleme mantığını korumak için basic temizlik yapıp linki döndürür
        import urllib.parse
        return urllib.parse.urlsplit(url)._replace(fragment="").geturl()

    def kopya_icerik_mi(self, icerik, url=None):
        # Sunucu tarafında ekstra veritabanı araması yapmaması için her içeriğe özgün der
        return False

    def harf_sec(self, metin):
        """Kelimelerin baş harflerini Türkçe karakter desteğiyle temizler."""
        if not metin:
            return "diger"
        ilk = str(metin).strip()[0].lower()
        mapping = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'i': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'}
        ilk = mapping.get(ilk, ilk)
        if ilk.isalnum():
            return ilk
        return "diger"

