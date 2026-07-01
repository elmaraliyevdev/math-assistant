import { Link, useSearch } from '@tanstack/react-router'
import { useEffect } from 'react'

import { AuthLayout } from '@/components/public/AuthLayout'
import { PageMeta } from '@/components/seo/PageMeta'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useVerifyEmail } from '@/features/auth/use-auth'

export function VerifyEmailPage() {
  const { token } = useSearch({ from: '/verify-email' })
  const verify = useVerifyEmail()

  useEffect(() => {
    if (token) {
      verify.mutate({ token })
    }
  }, [token])

  return (
    <AuthLayout>
      <PageMeta title="Verify Email" path="/verify-email" noIndex />
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Email verification</CardTitle>
        </CardHeader>
        <CardContent>
          {!token ? (
            <p className="text-sm text-muted-foreground">Invalid verification link.</p>
          ) : verify.isPending ? (
            <p className="text-sm text-muted-foreground">Verifying your email…</p>
          ) : verify.isSuccess ? (
            <div>
              <p className="text-sm text-muted-foreground">Your email has been verified.</p>
              <Button className="mt-4 w-full" asChild>
                <Link to="/dashboard">Go to dashboard</Link>
              </Button>
            </div>
          ) : (
            <p className="text-sm text-destructive">
              Verification failed. The link may have expired.
            </p>
          )}
        </CardContent>
      </Card>
    </AuthLayout>
  )
}
