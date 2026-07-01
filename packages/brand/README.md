# @math-assistant/brand

Canonical MathStudio branding assets and a framework-agnostic `Logo` component.

## Assets

Source files live in `assets/`:

- `logo.svg` — full wordmark (light backgrounds)
- `logo-white.svg` — full wordmark (dark backgrounds)
- `black-logo-icon.svg` — square icon (light backgrounds)
- `white-logo-icon.svg` — square icon (dark backgrounds)
- `favicon.svg` — derived from the white icon mark

## Sync

Copies assets to `packages/web` and `math-studio-lp` public folders:

```bash
npm run sync
# or: node scripts/sync-assets.mjs
```

`packages/web` `npm run sync:brand` delegates to this script.
