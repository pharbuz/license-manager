import { QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import type { PropsWithChildren } from "react";
import { AuthProvider } from "../auth";
import { createQueryClient } from "./query-client";

export function AppProviders({ children }: PropsWithChildren) {
  const [queryClient] = useState(() => createQueryClient());

  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </AuthProvider>
  );
}
