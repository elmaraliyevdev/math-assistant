import { Link } from '@tanstack/react-router'

import logoWhiteUrl from '@/assets/brand/logo-white.svg'
import logoUrl from '@/assets/brand/logo.svg'
import iconWhiteUrl from '@/assets/brand/white-logo-icon.svg'
import iconUrl from '@/assets/brand/black-logo-icon.svg'
import { SITE } from '@/lib/site-config'
import { useThemeStore } from '@/stores/theme-store'
import { cn } from '@/lib/utils'

export function Logo({
  variant = 'full',
  className,
  iconClassName,
  to = '/dashboard',
}: {
  variant?: 'full' | 'icon'
  className?: string
  iconClassName?: string
  to?: string | null
}) {
  const resolvedTheme = useThemeStore((state) => state.resolvedTheme)
  const isDark = resolvedTheme === 'dark'

  const src =
    variant === 'full'
      ? isDark
        ? logoWhiteUrl
        : logoUrl
      : isDark
        ? iconWhiteUrl
        : iconUrl

  const image = (
    <img
      src={src}
      alt={SITE.name}
      className={cn(
        variant === 'full' ? 'h-6 w-auto max-w-[10rem]' : 'h-8 w-8',
        iconClassName,
      )}
    />
  )

  const content = (
    <span className={cn('inline-flex items-center', className)}>{image}</span>
  )

  if (!to) return content

  return (
    <Link to={to} className="inline-flex transition-opacity duration-200 hover:opacity-80">
      {content}
    </Link>
  )
}
