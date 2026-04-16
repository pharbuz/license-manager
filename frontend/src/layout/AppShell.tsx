import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  Boxes,
  Building2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  Menu,
  PackageSearch,
  ScanSearch,
  ShieldCheck,
  UserSquare2,
  Users,
  X,
  type LucideIcon,
} from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { navItems } from "../app/routes";
import { useAuth } from "../auth";
import { PageTransition } from "../components/common";
import { getHealth } from "../services";
import { Breadcrumbs } from "./Breadcrumbs";
import { UserMenu } from "./UserMenu";
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

const iconByPath: Record<string, LucideIcon> = {
  "/": LayoutDashboard,
  "/licenses": ClipboardList,
  "/licenses/archived": ClipboardList,
  "/customers": Users,
  "/products": Building2,
  "/kinds": ShieldCheck,
  "/app-packages": PackageSearch,
  "/smtp-credentials": UserSquare2,
  "/audit/logs": ScanSearch,
};

export function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }

    const storage = window.localStorage;
    if (!storage || typeof storage.getItem !== "function") {
      return false;
    }

    return storage.getItem("sidebarCollapsed") === "true";
  });
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
  const { roles, user } = useAuth();
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 30000,
  });

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
    const storage = window.localStorage;
    if (storage && typeof storage.setItem === "function") {
      storage.setItem("sidebarCollapsed", String(sidebarCollapsed));
    }
  }, [sidebarCollapsed]);

  const sidebarSections = navSections.map((section) => ({
    ...section,
    items: navItems
      .filter((item) => (section.items as readonly string[]).includes(item.to))
      .map((item) => ({
        ...item,
        icon: iconByPath[item.to] ?? LayoutDashboard,
      })),
  }));

  const statusLabel =
    healthQuery.data?.status === "degraded" ? "Degraded" : "Online";
  const statusTone =
    healthQuery.data?.status === "degraded"
      ? "bg-amber-500 shadow-amber-500/25"
      : "bg-emerald-500 shadow-emerald-500/25";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-slate-50">
      {mobileNavOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-slate-950/50 backdrop-blur-sm lg:hidden"
          aria-label="Close navigation"
          onClick={() => setMobileNavOpen(false)}
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex h-full flex-col border-r border-slate-200/80 bg-white/95 shadow-xl shadow-slate-950/5 backdrop-blur transition-all duration-200 dark:border-slate-800 dark:bg-slate-900/95 ${
          mobileNavOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        } ${sidebarCollapsed ? "w-20" : "w-72"}`}
      >
        <div
          className={`border-b border-slate-200/80 dark:border-slate-800 ${sidebarCollapsed ? "px-3 py-5" : "px-4 py-5"}`}
        >
          <div
            className={`flex items-center ${sidebarCollapsed ? "justify-center" : "gap-3"}`}
          >
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 text-white shadow-lg shadow-blue-500/25">
              <Boxes className="h-5 w-5" />
            </div>
            {!sidebarCollapsed ? (
              <div className="min-w-0">
                <h1 className="truncate text-lg font-bold tracking-tight text-slate-950 dark:text-white">
                  License Manager
                </h1>
              </div>
            ) : null}
          </div>

          {!sidebarCollapsed && user ? (
            <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 dark:border-slate-800 dark:bg-slate-950/60">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/25" />
                <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
                  Active session
                </span>
              </div>
              <p className="mt-2 truncate text-sm font-medium text-slate-900 dark:text-white">
                {user.name ?? user.username ?? "Authenticated user"}
              </p>
              <p className="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">
                {roles.length > 0 ? roles.join(", ") : "Standard access"}
              </p>
            </div>
          ) : null}
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {sidebarSections.map((section, sectionIndex) => (
            <div key={section.name} className={sectionIndex > 0 ? "mt-5" : ""}>
              {!sidebarCollapsed ? (
                <p className="px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">
                  {section.name}
                </p>
              ) : null}

              <div className="space-y-1.5">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end
                      title={sidebarCollapsed ? item.label : undefined}
                      className={({ isActive }) =>
                        `group flex items-center rounded-2xl px-3 py-2.5 text-sm font-medium transition ${
                          sidebarCollapsed ? "justify-center" : "gap-3"
                        } ${
                          isActive
                            ? "bg-blue-50 text-blue-700 shadow-sm ring-1 ring-inset ring-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:ring-blue-900"
                            : "text-slate-700 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
                        }`
                      }
                      onClick={() => setMobileNavOpen(false)}
                    >
                      <Icon className="h-5 w-5 shrink-0" />
                      {!sidebarCollapsed ? (
                        <span className="truncate">{item.label}</span>
                      ) : null}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-slate-200/80 px-3 py-3 dark:border-slate-800">
          {!sidebarCollapsed ? (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3 dark:border-slate-800 dark:bg-slate-950/60">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400 dark:text-slate-500">
                System status
              </p>
              <div className="mt-2 flex items-center gap-2 text-sm font-medium text-slate-800 dark:text-slate-100">
                <span
                  className={`h-2.5 w-2.5 rounded-full shadow-lg ${statusTone}`}
                />
                <span>{statusLabel}</span>
              </div>
              <div className="mt-3 space-y-1.5 text-xs text-slate-500 dark:text-slate-400">
                <StatusRow
                  label="Postgres"
                  isHealthy={healthQuery.data?.services.postgres === "ok"}
                />
                <StatusRow
                  label="Key Vault"
                  isHealthy={healthQuery.data?.services.keyVault === "ok"}
                />
              </div>
            </div>
          ) : (
            <div className="flex justify-center">
              <span
                className={`h-3 w-3 rounded-full shadow-lg ${statusTone}`}
              />
            </div>
          )}

          <button
            type="button"
            className={`mt-3 hidden w-full items-center rounded-2xl px-3 py-2 text-sm text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white lg:flex ${
              sidebarCollapsed ? "justify-center" : "gap-2"
            }`}
            onClick={() => setSidebarCollapsed((value) => !value)}
            aria-label={
              sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"
            }
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <>
                <ChevronLeft className="h-4 w-4" />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>

      <div
        className={`transition-all duration-200 ${sidebarCollapsed ? "lg:pl-20" : "lg:pl-72"}`}
      >
        <header className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/85 backdrop-blur dark:border-slate-800 dark:bg-slate-900/85">
          <div className="flex min-h-18 items-center gap-4 px-4 py-3 sm:px-6 lg:px-8">
            <button
              type="button"
              className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:border-blue-200 hover:text-slate-950 lg:hidden dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-slate-600 dark:hover:text-white"
              aria-label="Toggle navigation"
              aria-expanded={mobileNavOpen}
              onClick={() => setMobileNavOpen((value) => !value)}
            >
              {mobileNavOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </button>

            <div className="min-w-0 flex-1">
              <Breadcrumbs />
            </div>

            <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-600 md:inline-flex dark:border-slate-700 dark:bg-slate-950 dark:text-slate-300">
              <span
                className={`h-2.5 w-2.5 rounded-full shadow-lg ${statusTone}`}
              />
              <span>{statusLabel}</span>
            </div>

            <UserMenu
              isDark={isDark}
              onToggleDarkMode={() => setIsDark((value) => !value)}
            />
          </div>
        </header>

        <main className="min-h-[calc(100vh-73px)]">
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>
    </div>
  );
}

function StatusRow({
  isHealthy,
  label,
}: {
  isHealthy: boolean;
  label: string;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span>{label}</span>
      <span
        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-medium ${
          isHealthy
            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300"
            : "bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300"
        }`}
      >
        {isHealthy ? (
          <ChevronRight className="h-3 w-3 rotate-90" />
        ) : (
          <AlertCircle className="h-3 w-3" />
        )}
        <span>{isHealthy ? "Healthy" : "Issue"}</span>
      </span>
    </div>
  );
}
