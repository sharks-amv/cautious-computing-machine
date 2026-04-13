import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'BB84 Analytics Dashboard',
  description: 'Modern dashboard for BB84 simulations'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
