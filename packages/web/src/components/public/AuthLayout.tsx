import { Logo } from '@/components/logo'

export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-muted/20">
      <header className="border-b bg-background px-4 py-4 md:px-6">
        <Logo variant="full" to="/" />
      </header>
      <div className="flex flex-1 items-center justify-center p-4">{children}</div>
    </div>
  )
}
