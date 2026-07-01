import { api } from '@/services/api'

export interface ContactSubmission {
  id: string
  type: string
  name: string
  email: string
  company?: string | null
  message: string
  status: string
  createdAt: string
}

export const contactService = {
  async submit(input: {
    type: string
    name: string
    email: string
    company?: string
    message: string
  }): Promise<{ id: string }> {
    const { data } = await api.post<{ id: string }>('/contact', input)
    return data
  },

  async listSubmissions(): Promise<{ items: ContactSubmission[]; total: number }> {
    const { data } = await api.get<{ items: ContactSubmission[]; total: number }>(
      '/admin/contact-submissions',
    )
    return data
  },
}
