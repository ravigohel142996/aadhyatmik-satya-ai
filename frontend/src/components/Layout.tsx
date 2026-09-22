import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Home" },
  { to: "/ask", label: "Ask" },
  { to: "/granth", label: "The Granth" },
  { to: "/how", label: "How It Works" },
  { to: "/about", label: "About" },
];

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-30 border-b border-black/5 bg-[#f6f0e6]/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-3">
          <NavLink to="/" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-full border border-[#c6a15b] text-[#6e2a38]">
              <Lotus />
            </span>
            <span>
              <span className="block font-dev text-lg leading-none text-ink">आध्यात्मिक सत्य</span>
              <span className="kicker">Source-grounded guide</span>
            </span>
          </NavLink>
          <nav className="flex flex-wrap justify-end gap-x-4 gap-y-1 text-sm text-[#5c4e43]">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.to === "/"}
                className={({ isActive }) =>
                  isActive ? "text-maroon" : "hover:text-ink"
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t border-black/5 px-5 py-8 text-center text-sm text-[#6d5e52]">
        <p className="font-display text-xl text-maroon">प्रश्न आपका — संदर्भ ग्रंथ का।</p>
        <p className="mx-auto mt-2 max-w-xl">
          A book-grounded digital guide. It does not speak as Swamiji, and it does not replace a living teacher.
        </p>
        <p className="mt-3">
          <NavLink to="/privacy" className="underline decoration-[#c6a15b] underline-offset-4">
            Privacy
          </NavLink>
        </p>
      </footer>
    </div>
  );
}

function Lotus() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3c.6 2.4.4 3.6 0 5-2.6.4-4.4 2.4-4.4 5 0 1.6.8 2.9 2 3.6C7.8 17.2 6 18.6 6 20.5h12c0-1.9-1.8-3.3-3.6-3.9 1.2-.7 2-2 2-3.6 0-2.6-1.8-4.6-4.4-5-.4-1.4-.6-2.6 0-5z"
        stroke="#6E2A38"
        strokeWidth="1.2"
      />
    </svg>
  );
}
