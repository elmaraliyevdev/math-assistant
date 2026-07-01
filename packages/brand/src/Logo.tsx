import type { AnchorHTMLAttributes, ReactNode } from 'react'

import { BRAND, resolveBrandAsset, type BrandTheme, type LogoVariant } from './brand'

export type LogoProps = {
  /** `full` wordmark or `icon` square mark */
  variant?: LogoVariant
  /** Controls which logo SVG is selected */
  theme?: BrandTheme
  /**
   * Public URL or bundled import URL for the logo image.
   * Consumers pass resolved paths from their bundler or `/logo.svg` in public/.
   */
  src: string
  className?: string
  iconClassName?: string
  /** Wrap in a link when provided */
  href?: string
  linkComponent?: 'a'
  children?: ReactNode
} & Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href' | 'children'>

function LogoImage({
  src,
  variant,
  className,
  iconClassName,
}: {
  src: string
  variant: LogoVariant
  className?: string
  iconClassName?: string
}) {
  return (
    <img
      src={src}
      alt={BRAND.name}
      className={
        variant === 'full'
          ? (className ?? 'h-6 w-auto max-w-[10rem]')
          : (iconClassName ?? className ?? 'h-8 w-8')
      }
    />
  )
}

/**
 * Framework-agnostic logo. Pass a resolved `src` from your bundler or public folder.
 *
 * @example
 * // Vite
 * import logoUrl from '@math-assistant/brand/assets/logo.svg'
 * <Logo src={logoUrl} theme="light" />
 *
 * @example
 * // Next.js public folder (after sync)
 * <Logo src="/logo.svg" theme="light" href="/" />
 */
export function Logo({
  variant = 'full',
  theme = 'light',
  src,
  className,
  iconClassName,
  href,
  linkComponent: _linkComponent = 'a',
  children,
  ...linkProps
}: LogoProps) {
  const image = (
    <LogoImage
      src={src}
      variant={variant}
      className={className}
      iconClassName={iconClassName}
    />
  )

  if (href) {
    return (
      <a href={href} className="inline-flex shrink-0 items-center" {...linkProps}>
        {image}
        {children}
      </a>
    )
  }

  return (
    <span className="inline-flex shrink-0 items-center">
      {image}
      {children}
    </span>
  )
}

export { resolveBrandAsset }
