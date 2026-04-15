## Post-implementation checks for AI agents

After implementing any code changes, always run these validation commands:

```bash
yarn -s tsc -p <project-root>/ui/tsconfig.json --noEmit --pretty false
yarn eslint <project-root>/<component-path>/<component-name>.tsx
```

Then format the project with Prettier:

```bash
npx prettier <project-root> --write
```

If Prettier is not available in the project, install it automatically before formatting (for example as a dev dependency), then run the formatting command again.
