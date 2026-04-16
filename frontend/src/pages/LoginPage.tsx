export function LoginPage() {
  return (
    <section className="login-page">
      <div className="login-page__card">
        <span className="login-page__pill">Protected Boundary Ready</span>
        <h1>License Manager Sign In</h1>
        <p>
          Authentication integration is intentionally abstracted until API-level
          auth contracts are confirmed.
        </p>
        <button className="login-page__button" type="button">
          Continue
        </button>
      </div>
    </section>
  );
}
