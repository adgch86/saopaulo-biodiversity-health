import type { Metadata } from "next";
import localFont from "next/font/local";
import { NextIntlClientProvider } from 'next-intl';
import { getLocale, getMessages } from 'next-intl/server';
import "./globals.css";
import "leaflet/dist/leaflet.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "TerraRisk Workshop | SEMIL-USP 2026",
  description: "Plataforma interativa para explorar o nexo Governança-Biodiversidade-Clima-Saúde em São Paulo",
  icons: {
    icon: "/favicon.ico",
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  const messages = await getMessages() as Record<string, unknown>;

  // Only pass common and categories to global provider
  // Pages will lazy-load their specific namespaces
  const layoutMessages = {
    common: messages.common,
    categories: messages.categories,
  };

  return (
    <html lang={locale}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <NextIntlClientProvider messages={layoutMessages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
