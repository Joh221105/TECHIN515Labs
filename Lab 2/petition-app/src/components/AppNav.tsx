"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Petitions" },
  { href: "/courses", label: "Courses" },
] as const;

export function AppNav() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/75 backdrop-blur-md">
      <nav className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3.5 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="group flex items-center gap-2 text-sm font-semibold text-slate-900 transition-colors hover:text-indigo-700"
        >
          <span
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-xs font-bold text-white shadow-sm shadow-indigo-900/25 transition-transform group-hover:scale-105"
            aria-hidden
          >
            CP
          </span>
          <span className="hidden sm:inline">Course Petition Tool</span>
          <span className="sm:hidden">Petitions</span>
        </Link>
        <div className="flex items-center gap-1 rounded-full bg-slate-100/90 p-1 ring-1 ring-slate-200/60">
          {links.map(({ href, label }) => {
            const active =
              href === "/"
                ? pathname === "/" || pathname.startsWith("/petition")
                : pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                key={href}
                href={href}
                className={
                  active
                    ? "rounded-full bg-white px-4 py-2 text-sm font-medium text-indigo-700 shadow-sm ring-1 ring-slate-200/80"
                    : "rounded-full px-4 py-2 text-sm font-medium text-slate-600 transition-colors hover:text-slate-900"
                }
              >
                {label}
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
