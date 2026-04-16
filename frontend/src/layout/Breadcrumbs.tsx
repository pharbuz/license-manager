import { ChevronRight, Home } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { navItems } from "../app/routes";

type BreadcrumbItem = {
  label: string;
  href?: string;
};

export function Breadcrumbs() {
  const location = useLocation();
  const pathSegments = location.pathname.split("/").filter(Boolean);

  if (pathSegments.length === 0) {
    return null;
  }

  const currentNavItem =
    [...navItems]
      .sort((left, right) => right.to.length - left.to.length)
      .find((item) => item.to === location.pathname) ?? null;

  const items: BreadcrumbItem[] = [{ label: "Home", href: "/" }];

  if (currentNavItem) {
    items.push({ label: currentNavItem.label });
  } else {
    const currentPath = `/${pathSegments.join("/")}`;
    items.push({
      label: formatSegment(
        pathSegments[pathSegments.length - 1] ?? currentPath,
      ),
    });
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <div
            key={`${item.label}-${index}`}
            className="flex items-center gap-1"
          >
            {index > 0 ? (
              <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
            ) : null}

            {item.href && !isLast ? (
              <Link
                to={item.href}
                className="flex items-center gap-1 text-slate-500 transition-colors hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
              >
                {index === 0 ? <Home className="h-3.5 w-3.5" /> : null}
                <span>{item.label}</span>
              </Link>
            ) : (
              <span
                className={`flex items-center gap-1 ${
                  isLast
                    ? "font-medium text-slate-950 dark:text-white"
                    : "text-slate-500 dark:text-slate-400"
                }`}
              >
                {index === 0 ? <Home className="h-3.5 w-3.5" /> : null}
                <span>{item.label}</span>
              </span>
            )}
          </div>
        );
      })}
    </nav>
  );
}

function formatSegment(segment: string) {
  return segment
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
