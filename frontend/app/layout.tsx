import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import HeroSection from "../components/HeroSection";
import Feedback from "../components/Feedback";

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
  title: "HealthBot",
  description: "A helpful assistant for your health queries",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex flex-col min-h-screen`}
      >
        {/* Header Section */}
        <header className="flex items-center justify-center bg-white py-4 shadow-md">
          <h1 className="text-blue-600 text-xl font-bold">HealthBot</h1>
        </header>

        {/* Hero Section */}
        <HeroSection />

        {/* Main Content */}
        <main className="flex-grow flex justify-center items-center px-4">
          {children}
        </main>

        {/* Feedback Section */}
        <Feedback />
      </body>
    </html>
  );
}
