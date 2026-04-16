import { Menu, X } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { navItems } from "../app/routes";
import { useAuth } from "../auth";
import "./app-shell.css";

export function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();
  const currentSection =
    navItems.find((item) =>
      item.to === "/"
        ? location.pathname === "/"
        : location.pathname.startsWith(item.to),
    ) ?? navItems[0];

  return (
    <div className="lm-shell">
      <aside className={`lm-shell__sidebar ${mobileNavOpen ? "is-open" : ""}`}>
        <div className="lm-shell__brand-block">
          <div className="lm-shell__brand">License Manager</div>
          <p className="lm-shell__brand-copy">
            Operational control panel for licenses, customers, and packages.
          </p>
        </div>
        <nav>
          <ul className="lm-shell__nav-list">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    isActive
                      ? "lm-shell__nav-link is-active"
                      : "lm-shell__nav-link"
                  }
                  onClick={() => setMobileNavOpen(false)}
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="lm-shell__sidebar-footer">
          <span className="lm-shell__sidebar-kicker">Current area</span>
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
            Connected to License Manager API
          </div>

          <div className="lm-shell__auth">
            <span className="lm-shell__user">
              {user?.name ?? user?.username ?? "Authenticated user"}
            </span>
            <button
              className="lm-shell__logout"
              type="button"
              onClick={() => void logout()}
            >
              Logout
            </button>
          </div>
        </header>

        <main className="lm-shell__main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
