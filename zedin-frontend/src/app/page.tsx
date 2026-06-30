'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const [sorgu, setSorgu] = useState('');
  const [aktifLens, setAktifLens] = useState('genel');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!sorgu.trim()) return;
    // Sorguyu ve lensi URL'e paslayarak sonuçlar sayfasına yönlendiriyoruz
    router.push(`/sonuclar?q=${encodeURIComponent(sorgu.trim())}&lens=${aktifLens}`);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#f9f9f8] dark:bg-[#0f172a] text-[#1a1a1a] dark:text-[#f9fafb] px-4 transition-colors duration-200">
      
      {/* Üst Sağ Küçük Navigasyon */}
      <div className="absolute top-6 right-6">
        <button className="text-xs font-medium border border-gray-300 dark:border-gray-700 px-3 py-1.5 rounded-full hover:border-purple-500 dark:hover:border-purple-400 transition-all">
          ⚙️ Ayarlar
        </button>
      </div>

      {/* Zedin. Logo */}
      <h1 className="text-6xl font-black tracking-tighter text-purple-700 dark:text-purple-400 mb-8 select-none">
        Zedin<span className="text-green-500">.</span>
      </h1>

      {/* Arama Kutusu Grubu */}
      <div className="w-full max-w-2xl">
        <form onSubmit={handleSearch} className="flex items-center bg-white dark:bg-[#1e293b] border-2 border-gray-200 dark:border-gray-800 rounded-2xl p-2 pl-5 focus-within:border-purple-600 dark:focus-within:border-purple-500 shadow-sm focus-within:shadow-md transition-all">
          <input
            type="text"
            value={sorgu}
            onChange={(e) => setSorgu(e.target.value)}
            placeholder="Ara veya kısayolları (!w, !yt) kullan..."
            className="w-full bg-transparent border-none outline-none text-base bg-clip-text"
            autoFocus
          />
          <button type="submit" className="bg-purple-700 hover:bg-purple-600 dark:bg-purple-600 dark:hover:bg-purple-500 text-white font-semibold text-sm px-6 py-3 rounded-xl transition-colors">
            Ara
          </button>
        </form>

        {/* Kagi Tarzı Lensler */}
        <div className="flex gap-2 justify-center mt-5">
          {['genel', 'forum', 'kod', 'akademik'].map((lens) => (
            <button
              key={lens}
              type="button"
              onClick={() => setAktifLens(lens)}
              className={`text-xs font-semibold px-4 py-2 rounded-full border transition-all capitalized ${
                aktifLens === lens
                  ? 'bg-purple-700 border-purple-700 text-white shadow-sm'
                  : 'bg-white dark:bg-[#1e293b] border-gray-200 dark:border-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-50'
              }`}
            >
              {lens === 'genel' && '🌐 '}
              {lens === 'forum' && '💬 '}
              {lens === 'kod' && '💻 '}
              {lens === 'akademik' && '🎓 '}
              {lens.charAt(0).toUpperCase() + lens.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Alt Bilgi */}
      <div className="mt-16 text-xs text-gray-400 dark:text-gray-500 tracking-wide font-medium">
        🔒 %100 MAHREMİYET • REKLAMSIZ • TAKİPÇİSİZ • LOKAL KONTROL
      </div>
    </div>
  );
}

