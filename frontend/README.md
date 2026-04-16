# License Manager Frontend

Frontend application for License Manager built with React, TypeScript, Vite, React Router, and React Query.

## Commands

- `yarn dev` - start local development server
- `yarn typecheck` - run TypeScript project checks
- `yarn lint` - run ESLint
- `yarn test` - run tests in watch mode
- `yarn test:run` - run tests once
- `yarn build` - create a production build

## Keycloak configuration

1. Copy `.env.example` to `.env` and fill:

- `VITE_API_BASE_URL`
- `VITE_KEYCLOAK_URL`
- `VITE_KEYCLOAK_REALM`
- `VITE_KEYCLOAK_CLIENT_ID`

2. In Keycloak client settings configure:

- `Valid redirect URIs`: `http://localhost:5173/*` (and your production app URL)
- `Web origins`: `http://localhost:5173` (or `+` if your Keycloak policy allows it)

3. Run frontend with `yarn dev`.

## Authentication flow (SPA)

- Public route: `/login`
- Private routes: all dashboard routes behind auth guard
- Login: redirect to Keycloak (`keycloak-js`)
- Session restore: `check-sso` on app startup
- Token refresh: before API requests and periodically in background
- Logout: Keycloak logout endpoint with redirect back to `/login`

## Stage 1 bootstrap structure

- `src/app` - application bootstrap, router, providers
- `src/components` - reusable UI components
- `src/features` - feature-level hooks and modules
- `src/hooks` - cross-feature hooks
- `src/layout` - shell and navigation layout
- `src/pages` - route-level pages
- `src/services` - API services (next stage)
- `src/types` - API and domain types (next stage)
- `src/utils` - shared helpers
