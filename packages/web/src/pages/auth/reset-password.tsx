import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useSearch } from '@tanstack/react-router'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { AuthLayout } from '@/components/public/AuthLayout'
import { PageMeta } from '@/components/seo/PageMeta'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useResetPassword } from '@/features/auth/use-auth'
import { getErrorMessage } from '@/services/api'

const schema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
})

type Form = z.infer<typeof schema>

export function ResetPasswordPage() {
  const { token } = useSearch({ from: '/reset-password' })
  const reset = useResetPassword()
  const { register, handleSubmit, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
  })

  if (!token) {
    return (
      <AuthLayout>
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Invalid reset link.</p>
            <Link to="/forgot-password" className="mt-4 inline-block text-sm text-primary hover:underline">
              Request a new link
            </Link>
          </CardContent>
        </Card>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout>
      <PageMeta title="Reset Password" path="/reset-password" noIndex />
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Choose a new password</CardTitle>
        </CardHeader>
        <CardContent>
          {reset.isSuccess ? (
            <div>
              <p className="text-sm text-muted-foreground">Your password has been updated.</p>
              <Button className="mt-4 w-full" asChild>
                <Link to="/login">Sign in</Link>
              </Button>
            </div>
          ) : (
            <form
              className="space-y-4"
              onSubmit={handleSubmit((values) =>
                reset.mutate({ token, password: values.password }),
              )}
            >
              <div className="space-y-2">
                <Label htmlFor="password">New password</Label>
                <Input id="password" type="password" {...register('password')} />
                {errors.password && (
                  <p className="text-sm text-destructive">{errors.password.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm password</Label>
                <Input id="confirmPassword" type="password" {...register('confirmPassword')} />
                {errors.confirmPassword && (
                  <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
                )}
              </div>
              {reset.isError && (
                <p className="text-sm text-destructive">{getErrorMessage(reset.error)}</p>
              )}
              <Button className="w-full" type="submit" disabled={reset.isPending}>
                {reset.isPending ? 'Updating…' : 'Update password'}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </AuthLayout>
  )
}
