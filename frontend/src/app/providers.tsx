import { QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import type { PropsWithChildren } from "react";
import { AuthProvider } from "../auth";
import { initializeTheme } from "../utils/theme";
import { createQueryClient } from "./query-client";

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(() => createQueryClient());

  useEffect(() => {
    initializeTheme();
  }, []);

  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </AuthProvider>
  );
}
