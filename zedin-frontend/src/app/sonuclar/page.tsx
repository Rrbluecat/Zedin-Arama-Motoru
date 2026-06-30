'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, Suspense } from 'react';

// 🧠 1. Senin mevcut arama motoru arayüzün ve tüm mantığın burada (Zerre değişmedi)
function ResultsContent() {
  const searchParams = useSearchParams();
  const q = searchParams.get('q') || '';
  const lens = searchParams.get('lens') || 'genel';
  const [sorgu, setSorgu] = useState(q);
  const [yukleniyor, setYukleniyor] = useState(true);

  useEffect(() => {
    // Burada Python API'sine (/api/indeks) istek atıp sonuçları çekeceğiz
    setYukleniyor(false);
  }, [q, lens]);

  return (
    <div className="min-h-screen bg-[#f9f9f8] dark:bg-[#0f172a] text-[#1a1a1a] dark:text-[#f9fafb]">
      {/* Üst Yapışkan Header */}
      <header className="sticky top-0 z-50 bg-white dark:bg-[#1e293b] border-b border-gray-200 dark:border-gray-800 shadow-sm px-6 py-4 flex items-center gap-6">
        <a href="/" className="text-2xl font-black tracking-tighter text-purple-700 dark:text-purple-400 select-none">
          Zedin<span className="text-green-500">.</span>
        </a>
        <form className="flex-1 max-w-2xl flex items-center bg-[#f3f4f6] dark:bg-[#0f172a] rounded-xl px-4 py-2 border border-transparent focus-within:border-purple-500 transition-all">
          <input
            type="text"
            value={sorgu}
            onChange={(e) => setSorgu(e.target.value)}
            className="w-full bg-transparent border-none outline-none text-sm text-gray-900 dark:text-gray-100"
          />
          <button type="submit" className="text-xs font-bold text-purple-700 dark:text-purple-400 ml-2">Ara</button>
        </form>
      </header>

      {/* İki Sütunlu Ana Gövde */}
      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sol Sütun: Arama Sonuçları (Max Genişlik Kuralı Uygulandı) */}
        <section className="lg:col-span-2 max-w-2xl w-full">
          <div className="text-xs text-gray-400 dark:text-gray-500 mb-6 font-medium">
            &quot;{q}&quot; için 20 sonuç listelendi — {lens} lensi aktif
          </div>

          {/* Zedin AI Akıllı Yanıt Bloğu (Kagi Assistant Tarzı) */}
          <div className="bg-white dark:bg-[#1e293b] border border-purple-100 dark:border-purple-900/50 border-l-4 border-l-purple-700 dark:border-l-purple-500 rounded-xl p-5 mb-8 shadow-sm">
            <div className="text-[10px] font-bold tracking-wider text-purple-700 dark:text-purple-400 uppercase mb-1">🧠 ZEDIN AI ÖZETİ</div>
            <p className="text-sm font-medium leading-relaxed text-gray-700 dark:text-gray-300">
              Yapay zeka katmanı sonuçları sentezliyor... Termux lokal altyapısı optimize ediliyor.
            </p>
          </div>

          {/* Örnek Profesyonel Sonuç Kartı */}
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <article key={i} className="group py-2 border-b border-gray-100 dark:border-gray-800/50 last:border-none">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-4 h-4 bg-gray-200 dark:bg-gray-700 rounded-sm"></div>
                  <span className="text-xs text-green-600 dark:text-green-400 font-medium truncate max-w-md">https://github.com/zedin-arama/motoru</span>
                </div>
                <h3 className="text-lg font-semibold text-blue-700 dark:text-blue-400 group-hover:underline leading-snug mb-1">
                  <a href="#">Zedin Arama Motoru Çekirdek Yapısı - Örnek Sonuç {i}</a>
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  Kagi tarzı arama ekosisteminin filtrelenmiş ve indekslenmiş verileri burada listelenir. Bu tasarım yapay zeka tarafından rastgele fırlatılmış hissi vermez, tamamen nizami ve okunabilirdir...
                </p>
              </article>
            ))}
          </div>
        </section>

        {/* Sağ Sütun: Kagi Tarzı Yan Panel Kontrolleri */}
        <aside className="space-y-6">
          <div className="bg-white dark:bg-[#1e293b] border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
            <h4 className="text-xs font-bold text-gray-400 dark:text-gray-500 tracking-wider uppercase mb-4">Arayüz Kişiselleştirme</h4>
            <div className="space-y-4 text-xs font-medium text-gray-600 dark:text-gray-300">
              <div className="flex justify-between items-center">
                <span>Arama Yoğunluğu</span>
                <select className="bg-gray-50 dark:bg-[#0f172a] border border-gray-200 dark:border-gray-800 p-1.5 rounded-md outline-none">
                  <option>Normal (Standart)</option>
                  <option>Compact (Sıkışık)</option>
                  <option>Relaxed (Geniş)</option>
                </select>
              </div>
              <div className="flex justify-between items-center">
                <span>Faviconları Göster</span>
                <input type="checkbox" defaultChecked className="accent-purple-700" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-[#1e293b] border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm">
            <h4 className="text-xs font-bold text-gray-400 dark:text-gray-500 tracking-wider uppercase mb-3">Domain Puanlama (Ranking)</h4>
            <input type="text" placeholder="pinterest.com" className="w-full bg-gray-50 dark:bg-[#0f172a] border border-gray-200 dark:border-gray-800 text-xs p-2.5 rounded-lg mb-2 outline-none" />
            <button className="w-full bg-[#1a1a1a] dark:bg-purple-600 text-white text-xs font-bold py-2 rounded-lg hover:opacity-90 transition-opacity">
              Siteyi Engelle veya Öne Çıkar
             </button>
          </div>
        </aside>
      </main>
    </div>
  );
}

// 🛡️ 2. Next.js Derleyicisini Kurtaran Ana Yapı (Default Export)
export default function ResultsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#f9f9f8] dark:bg-[#0f172a] flex items-center justify-center text-sm font-medium text-gray-500">
        Zedin arama sonuçları yükleniyor...
      </div>
    }>
      <ResultsContent />
    </Suspense>
  );
}

