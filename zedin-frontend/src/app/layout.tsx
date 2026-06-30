import type { Metadata } from 'next';
// 🚀 Kullanıcının kendi lokal dosyası (Eğer varsa yüklenecek)
import '../../custom-zedin.css'; 

export const metadata: Metadata = {
  title: 'Zedin Arama Ekosistemi',
  description: 'Kişiselleştirilebilir, reklamsız, lokal arama motoru.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body className="antialiased selection:bg-purple-200">
        {children}
      </body>
    </html>
  );
}

