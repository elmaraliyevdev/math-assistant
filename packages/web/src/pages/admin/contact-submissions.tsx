import { useQuery } from '@tanstack/react-query'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { contactService } from '@/services/contact'

export function AdminContactPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin', 'contact'],
    queryFn: () => contactService.listSubmissions(),
    retry: false,
  })

  if (isLoading) {
    return <Skeleton className="h-64 w-full" />
  }

  if (isError) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            Admin access required. Set API_PLATFORM_ADMIN_EMAILS to your account email.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Contact submissions</h1>
        <p className="text-sm text-muted-foreground">{data?.total ?? 0} total</p>
      </div>
      <div className="space-y-4">
        {data?.items.map((item) => (
          <Card key={item.id}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">
                {item.name} · {item.type}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p className="text-muted-foreground">{item.email}</p>
              {item.company && <p>Company: {item.company}</p>}
              <p className="whitespace-pre-wrap">{item.message}</p>
              <p className="text-xs text-muted-foreground">
                {new Date(item.createdAt).toLocaleString()} · {item.status}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
