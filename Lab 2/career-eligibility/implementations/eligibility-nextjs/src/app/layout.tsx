import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GIX Quick Eligibility Checker",
  description: "See which GIX Career Services events you may qualify for.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
