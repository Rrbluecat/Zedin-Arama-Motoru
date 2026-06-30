'use client';
import { useEffect, useState } from 'react';

export default function CustomCssInjector() {
  const [customCss, setCustomCss] = useState('');

  useEffect(() => {
    // Sayfa yüklendiğinde lokal hafızadaki özel CSS'i çek
    const kayıtlıCss = localStorage.getItem('zedin-custom-css') || '';
    setCustomCss(kayıtlıCss);
    
    // Canlı olarak sayfaya enjekte et
    styleElementiniGuncelle(kayıtlıCss);
  }, []);

  const styleElementiniGuncelle = (cssMetni: string) => {
    let styleTag = document.getElementById('zedin-user-styles');
    if (!styleTag) {
      styleTag = document.createElement('style');
      styleTag.id = 'zedin-user-styles';
      document.head.appendChild(styleTag);
    }
    styleTag.innerHTML = cssMetni;
  };

  const cssKaydet = (yeniCss: string) => {
    setCustomCss(yeniCss);
    localStorage.setItem('zedin-custom-css', yeniCss);
    styleElementiniGuncelle(yeniCss);
  };

  return (
    <div className="bg-white dark:bg-[#1e293b] border border-gray-200 dark:border-gray-800 rounded-xl p-5 shadow-sm mt-4">
      <h4 className="text-xs font-bold text-gray-400 dark:text-gray-500 tracking-wider uppercase mb-2">
        🛠️ Gelişmiş CSS Enjeksiyonu (Lokal)
      </h4>
      <p className="text-[11px] text-gray-400 mb-3">
        Arayüzü tamamen değiştirecek CSS kodlarını buraya yazabilirsin. Canlı uygulanır.
      </p>
      <textarea
        value={customCss}
        onChange={(e) => cssKaydet(e.target.value)}
        placeholder="Örn: .result-item { border: 1px solid red; }"
        className="w-full h-32 bg-gray-50 dark:bg-[#0f172a] text-mono text-xs p-3 rounded-lg border border-gray-200 dark:border-gray-800 outline-none font-mono"
      />
    </div>
  );
}

