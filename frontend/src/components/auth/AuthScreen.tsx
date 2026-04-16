import type { PropsWithChildren } from "react";

type AuthScreenProps = PropsWithChildren<{
  size?: "default" | "wide";
}>;

export function AuthScreen({ children, size = "default" }: AuthScreenProps) {
  return (
    <section className="auth-screen">
      <div
        className={`auth-screen__content${
          size === "wide" ? " auth-screen__content--wide" : ""
        }`}
      >
        {children}
      </div>
    </section>
  );
}
