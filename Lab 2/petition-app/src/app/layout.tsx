import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AppNav } from "@/components/AppNav";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Course Petition Tool",
  description:
    "Validate syllabi, merge PDFs, run AI-assisted comparisons, and track course petitions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-slate-50 antialiased text-slate-900 [background-image:radial-gradient(at_100%_0%,rgb(238_242_255)_0px,transparent_50%),radial-gradient(at_0%_100%,rgb(241_245_249)_0px,transparent_55%)]`}
      >
        <AppNav />
        {children}
      </body>
    </html>
  );
}
