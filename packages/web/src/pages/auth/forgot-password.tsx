import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from '@tanstack/react-router'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { AuthLayout } from '@/components/public/AuthLayout'
import { PageMeta } from '@/components/seo/PageMeta'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useForgotPassword } from '@/features/auth/use-auth'
import { getErrorMessage } from '@/services/api'

const schema = z.object({
  email: z.email(),
})

type Form = z.infer<typeof schema>

export function ForgotPasswordPage() {
  const forgot = useForgotPassword()
  const { register, handleSubmit, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
  })

  return (
    <AuthLayout>
      <PageMeta title="Forgot Password" path="/forgot-password" noIndex />
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Reset your password</CardTitle>
        </CardHeader>
        <CardContent>
          {forgot.isSuccess ? (
            <p className="text-sm text-muted-foreground">
              If an account exists for that email, we sent a reset link. Check your
              inbox or server logs in development.
            </p>
          ) : (
            <form
              className="space-y-4"
              onSubmit={handleSubmit((values) => forgot.mutate(values))}
            >
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" autoComplete="email" {...register('email')} />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>
              {forgot.isError && (
                <p className="text-sm text-destructive">{getErrorMessage(forgot.error)}</p>
              )}
              <Button className="w-full" type="submit" disabled={forgot.isPending}>
                {forgot.isPending ? 'Sending…' : 'Send reset link'}
              </Button>
            </form>
          )}
          <p className="mt-4 text-center text-sm text-muted-foreground">
            <Link to="/login" className="text-primary hover:underline">Back to sign in</Link>
          </p>
        </CardContent>
      </Card>
    </AuthLayout>
  )
}
