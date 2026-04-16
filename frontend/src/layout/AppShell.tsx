import {
  Boxes,
  ChartNoAxesColumn,
  ChevronDown,
  ClipboardList,
  LayoutDashboard,
  Menu,
  Moon,
  ShieldCheck,
  Sun,
  Users,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { navItems } from "../app/routes";
import { useAuth } from "../auth";
import "./app-shell.css";

const navSections = [
  {
    name: "Main",
    items: ["/", "/licenses", "/licenses/archived"],
  },
  {
    name: "Management",
    items: ["/customers", "/products", "/kinds", "/app-packages"],
  },
  {
    name: "Operations",
    items: ["/smtp-credentials", "/audit/logs"],
  },
] as const;

const iconByPath: Record<string, typeof LayoutDashboard> = {
  "/": LayoutDashboard,
  "/licenses": ClipboardList,
  "/licenses/archived": ClipboardList,
  "/customers": Users,
  "/products": Boxes,
  "/kinds": ShieldCheck,
  "/app-packages": Boxes,
  "/smtp-credentials": ShieldCheck,
  "/audit/logs": ChartNoAxesColumn,
};

export function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }

    const storage = window.localStorage;
    if (!storage || typeof storage.getItem !== "function") {
      return document.documentElement.classList.contains("dark");
    }

    const saved = storage.getItem("darkMode");
    if (saved === null) {
      return document.documentElement.classList.contains("dark");
    }
    return saved === "true";
  });
  const userMenuRef = useRef<HTMLDivElement | null>(null);
  const location = useLocation();
  const { user, logout } = useAuth();
  const currentSection =
    navItems.find((item) =>
      item.to === "/"
        ? location.pathname === "/"
        : location.pathname.startsWith(item.to),
    ) ?? navItems[0];

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }

    const storage = window.localStorage;
    if (storage && typeof storage.setItem === "function") {
      storage.setItem("darkMode", String(isDark));
    }
  }, [isDark]);

  useEffect(() => {
    if (!userMenuOpen) {
      return;
    }

    const handleOutsideClick = (event: MouseEvent) => {
      if (!userMenuRef.current) {
        return;
      }

      const target = event.target;
      if (!(target instanceof Node)) {
        return;
      }

      if (!userMenuRef.current.contains(target)) {
        setUserMenuOpen(false);
      }
    };

    window.addEventListener("mousedown", handleOutsideClick);
    return () => window.removeEventListener("mousedown", handleOutsideClick);
  }, [userMenuOpen]);

  return (
    <div className="lm-shell">
      <aside className={`lm-shell__sidebar ${mobileNavOpen ? "is-open" : ""}`}>
        <div className="lm-shell__brand-block">
          <div className="lm-shell__brand-row">
            <div className="lm-shell__brand-icon">LM</div>
            <div>
              <div className="lm-shell__brand">License Manager</div>
              <p className="lm-shell__brand-copy">Operations Console</p>
            </div>
          </div>
        </div>

        <nav className="lm-shell__nav">
          {navSections.map((section) => (
            <div key={section.name} className="lm-shell__nav-section">
              <p className="lm-shell__section-title">{section.name}</p>
              <ul className="lm-shell__nav-list">
                {navItems
                  .filter((item) =>
                    (section.items as readonly string[]).includes(item.to),
                  )
                  .map((item) => {
                    const Icon = iconByPath[item.to] ?? LayoutDashboard;
                    return (
                      <li key={item.to}>
                        <NavLink
                          to={item.to}
                          end={item.to === "/" || item.to === "/licenses"}
                          className={({ isActive }) =>
                            isActive
                              ? "lm-shell__nav-link is-active"
                              : "lm-shell__nav-link"
                          }
                          onClick={() => setMobileNavOpen(false)}
                        >
                          <Icon size={18} />
                          <span>{item.label}</span>
                        </NavLink>
                      </li>
                    );
                  })}
              </ul>
            </div>
          ))}
        </nav>

        <div className="lm-shell__sidebar-footer">
          <span className="lm-shell__sidebar-kicker">Current View</span>
          <strong>{currentSection.label}</strong>
        </div>
      </aside>

      {mobileNavOpen ? (
        <button
          type="button"
          className="lm-shell__backdrop"
          aria-label="Close navigation"
          onClick={() => setMobileNavOpen(false)}
        />
      ) : null}

      <div className="lm-shell__content-wrap">
        <header className="lm-shell__topbar">
          <div className="lm-shell__topbar-left">
            <button
              className="lm-shell__toggle"
              type="button"
              aria-label="Toggle navigation"
              aria-expanded={mobileNavOpen}
              onClick={() => setMobileNavOpen((value) => !value)}
            >
              {mobileNavOpen ? <X size={18} /> : <Menu size={18} />}
            </button>

            <div>
              <div className="lm-shell__topbar-kicker">Current view</div>
              <div className="lm-shell__topbar-title">
                {currentSection.label}
              </div>
            </div>
          </div>

          <div className="lm-shell__status">
            <span className="lm-shell__status-dot" />
            System online
          </div>

          <div className="lm-shell__auth" ref={userMenuRef}>
            <button
              className="lm-shell__user-button"
              type="button"
              aria-haspopup="menu"
              aria-expanded={userMenuOpen}
              onClick={() => setUserMenuOpen((value) => !value)}
            >
              <span className="lm-shell__user-avatar">
                {(user?.name ?? user?.username ?? "U")[0]?.toUpperCase()}
              </span>
              <span className="lm-shell__user">
                {user?.name ?? user?.username ?? "Authenticated user"}
              </span>
              <ChevronDown size={16} />
            </button>

            {userMenuOpen ? (
              <div className="lm-shell__user-menu" role="menu">
                <button
                  className="lm-shell__user-menu-item"
                  type="button"
                  onClick={() => setIsDark((value) => !value)}
                >
                  {isDark ? <Sun size={16} /> : <Moon size={16} />}
                  <span>{isDark ? "Light mode" : "Dark mode"}</span>
                </button>
                <button
                  className="lm-shell__user-menu-item"
                  type="button"
                  onClick={() => void logout()}
                >
                  <span>Logout</span>
                </button>
              </div>
            ) : null}
          </div>
        </header>

        <main className="lm-shell__main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
