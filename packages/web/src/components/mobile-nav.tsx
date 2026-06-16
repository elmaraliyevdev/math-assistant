import { Link } from '@tanstack/react-router'
import { LogOut, Menu } from 'lucide-react'
import { useState } from 'react'

import { NAV_ITEMS } from '@/lib/navigation'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Separator } from '@/components/ui/separator'
import { useLogout } from '@/features/auth/use-auth'
import { cn } from '@/lib/utils'

export function MobileNav() {
  const [open, setOpen] = useState(false)
  const logout = useLogout()

  return (
    <>
      <Button
        variant="outline"
        size="icon"
        className="md:hidden"
        aria-label="Open navigation menu"
        onClick={() => setOpen(true)}
      >
        <Menu className="h-4 w-4" />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent
          className={cn(
            'fixed inset-y-0 left-0 top-0 h-full w-[min(100%,18rem)] max-w-none translate-x-0 translate-y-0 rounded-none border-r p-0',
            'data-[state=open]:animate-in data-[state=closed]:animate-out',
          )}
        >
          <DialogHeader className="border-b px-4 py-4 text-left">
            <DialogTitle>Math Assistant</DialogTitle>
            <p className="text-sm text-muted-foreground">Platform navigation</p>
          </DialogHeader>

          <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-4">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setOpen(false)}
                className="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground [&.active]:bg-accent [&.active]:text-accent-foreground"
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </nav>

          <div className="mt-auto border-t p-4">
            <Separator className="mb-4" />
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={() => {
                setOpen(false)
                logout.mutate()
              }}
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
