/**
 * Canonical MathStudio branding metadata.
 * Asset files live in `packages/brand/assets/`.
 */
export const BRAND = {
  name: 'MathStudio',
  tagline: 'The Operating System for Slot Game Mathematics',
  description:
    'Design reel strips, generate game versions, simulate millions of spins, calibrate RTP, collaborate with your team, and prepare certification — all from one platform.',
  url: 'https://mathstudio.app',
} as const

export type BrandTheme = 'light' | 'dark'

export type LogoVariant = 'full' | 'icon'

/** Filenames in `packages/brand/assets/` (also synced to app public folders). */
export const BRAND_ASSET_FILES = {
  logo: 'logo.svg',
  logoWhite: 'logo-white.svg',
  iconDark: 'black-logo-icon.svg',
  iconLight: 'white-logo-icon.svg',
  favicon: 'favicon.svg',
} as const

/**
 * Resolve the asset filename for a logo variant and color theme.
 * Full logos are wordmarks; icons are square marks for favicons and compact UI.
 */
export function resolveBrandAsset(
  variant: LogoVariant,
  theme: BrandTheme,
): (typeof BRAND_ASSET_FILES)[keyof typeof BRAND_ASSET_FILES] {
  if (variant === 'icon') {
    return theme === 'dark' ? BRAND_ASSET_FILES.iconLight : BRAND_ASSET_FILES.iconDark
  }
  return theme === 'dark' ? BRAND_ASSET_FILES.logoWhite : BRAND_ASSET_FILES.logo
}
