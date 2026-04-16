import {
  Content,
  Item,
  Portal,
  Root,
  Separator,
  Trigger,
} from "@radix-ui/react-dropdown-menu";
import {
  ChevronDown,
  Keyboard,
  LogOut,
  Moon,
  Sun,
  UserRound,
} from "lucide-react";
import { useAuth } from "../auth";

type UserMenuProps = {
  isDark: boolean;
  onToggleDarkMode: () => void;
};

export function UserMenu({ isDark, onToggleDarkMode }: UserMenuProps) {
  const { user, logout } = useAuth();
  const initials = (user?.name ?? user?.username ?? "U")
    .split(" ")
    .map((part) => part[0] ?? "")
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <Root>
      <Trigger asChild>
        <button
          type="button"
          className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-left shadow-sm transition hover:border-blue-200 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500/30 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-slate-600 dark:hover:bg-slate-800"
          aria-label="User menu"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-700 text-sm font-semibold text-white shadow-sm shadow-blue-500/30">
            {initials}
          </span>
          <span className="hidden min-w-0 sm:block">
            <span className="block max-w-40 truncate text-sm font-medium text-slate-900 dark:text-white">
              {user?.name ?? user?.username ?? "Authenticated user"}
            </span>
            <span className="block max-w-40 truncate text-xs text-slate-500 dark:text-slate-400">
              {user?.email ?? "Active session"}
            </span>
          </span>
          <ChevronDown className="h-4 w-4 text-slate-400" />
        </button>
      </Trigger>

      <Portal>
        <Content
          sideOffset={10}
          align="end"
          className="z-50 min-w-60 rounded-2xl border border-slate-200 bg-white p-1.5 shadow-2xl shadow-slate-950/10 outline-none dark:border-slate-700 dark:bg-slate-900"
        >
          <div className="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5 dark:border-slate-800 dark:bg-slate-950/60">
            <p className="truncate text-sm font-semibold text-slate-950 dark:text-white">
              {user?.name ?? user?.username ?? "Authenticated user"}
            </p>
            <p className="truncate text-xs text-slate-500 dark:text-slate-400">
              {user?.email ?? "No email claim"}
            </p>
          </div>

          <Item
            className="mt-1.5 flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-700 outline-none transition hover:bg-slate-100 focus:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800 dark:focus:bg-slate-800"
            onSelect={(event) => {
              event.preventDefault();
              onToggleDarkMode();
            }}
          >
            {isDark ? (
              <Sun className="h-4 w-4 text-amber-500" />
            ) : (
              <Moon className="h-4 w-4 text-blue-500" />
            )}
            <span>{isDark ? "Light mode" : "Dark mode"}</span>
          </Item>

          <Item
            className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-700 outline-none transition hover:bg-slate-100 focus:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800 dark:focus:bg-slate-800"
            onSelect={(event) => {
              event.preventDefault();
            }}
          >
            <Keyboard className="h-4 w-4 text-slate-400" />
            <span>Keyboard shortcuts</span>
            <span className="ml-auto text-xs text-slate-400">Soon</span>
          </Item>

          <Separator className="my-1 h-px bg-slate-200 dark:bg-slate-700" />

          <Item
            className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-sm text-slate-700 outline-none transition hover:bg-slate-100 focus:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800 dark:focus:bg-slate-800"
            onSelect={(event) => {
              event.preventDefault();
            }}
          >
            <UserRound className="h-4 w-4 text-slate-400" />
            <span>Profile</span>
            <span className="ml-auto text-xs text-slate-400">Soon</span>
          </Item>

          <Item
            className="flex cursor-pointer items-center gap-2 rounded-xl px-3 py-2 text-sm text-red-600 outline-none transition hover:bg-red-50 focus:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40 dark:focus:bg-red-950/40"
            onSelect={() => {
              void logout();
            }}
          >
            <LogOut className="h-4 w-4" />
            <span>Logout</span>
          </Item>
        </Content>
      </Portal>
    </Root>
  );
}
