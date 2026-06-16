import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import { simulationsApi } from '@/features/simulations/api/simulations-api'
import type {
  CreateSimulationInput,
  SimulationListParams,
} from '@/features/simulations/types'
import { toast } from '@/lib/toast'
import { getErrorMessage } from '@/services/api'

export const simulationKeys = {
  all: ['simulations'] as const,
  list: (params: SimulationListParams) => ['simulations', 'list', params] as const,
  detail: (simulationId: string) =>
    ['simulations', 'detail', simulationId] as const,
  results: (simulationId: string) =>
    ['simulations', 'results', simulationId] as const,
  compare: (simulationIds: string[]) =>
    ['simulations', 'compare', simulationIds.join(',')] as const,
  notes: (simulationId: string) =>
    ['simulations', 'notes', simulationId] as const,
}

const ACTIVE_STATUSES = new Set(['pending', 'running'])

export function isSimulationActive(status: string | undefined): boolean {
  return Boolean(status && ACTIVE_STATUSES.has(status))
}

export function useSimulations(params: SimulationListParams = {}) {
  return useQuery({
    queryKey: simulationKeys.list(params),
    queryFn: () => simulationsApi.list(params),
    refetchOnWindowFocus: true,
  })
}

export function useSimulation(simulationId: string, poll = false) {
  return useQuery({
    queryKey: simulationKeys.detail(simulationId),
    queryFn: () => simulationsApi.get(simulationId),
    enabled: Boolean(simulationId),
    refetchInterval: (query) => {
      if (!poll) return false
      return isSimulationActive(query.state.data?.status) ? 2000 : false
    },
    refetchOnWindowFocus: true,
  })
}

export function useSimulationResults(simulationId: string, enabled = true) {
  return useQuery({
    queryKey: simulationKeys.results(simulationId),
    queryFn: () => simulationsApi.getResults(simulationId),
    enabled: enabled && Boolean(simulationId),
    retry: false,
    refetchOnWindowFocus: true,
  })
}

export function useCreateSimulation(options?: { suppressNavigation?: boolean }) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const suppressNavigation = options?.suppressNavigation ?? false

  return useMutation({
    mutationFn: (input: CreateSimulationInput) => simulationsApi.create(input),
    onSuccess: async (result) => {
      await queryClient.invalidateQueries({ queryKey: simulationKeys.all })
      toast.success('Simulation started successfully')
      if (suppressNavigation) {
        return
      }
      await navigate({
        to: '/simulations/$simulationId',
        params: { simulationId: result.simulationId },
      })
    },
    onError: (error) => {
      toast.error(getErrorMessage(error))
    },
  })
}

export function useCancelSimulation(simulationId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => simulationsApi.cancel(simulationId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: simulationKeys.all })
      await queryClient.invalidateQueries({
        queryKey: simulationKeys.detail(simulationId),
      })
      toast.success('Cancellation requested')
    },
    onError: (error) => {
      toast.error(getErrorMessage(error))
    },
  })
}

export function useSimulationCompare(simulationIds: string[], enabled = true) {
  return useQuery({
    queryKey: simulationKeys.compare(simulationIds),
    queryFn: () => simulationsApi.compare(simulationIds),
    enabled: enabled && simulationIds.length >= 2,
    retry: false,
  })
}

export function useSimulationNotes(simulationId: string, enabled = true) {
  return useQuery({
    queryKey: simulationKeys.notes(simulationId),
    queryFn: () => simulationsApi.listNotes(simulationId),
    enabled: enabled && Boolean(simulationId),
  })
}

export function useCreateSimulationNote(simulationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (content: string) =>
      simulationsApi.createNote(simulationId, content),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: simulationKeys.notes(simulationId),
      })
      toast.success('Note added')
    },
    onError: (error) => {
      toast.error(getErrorMessage(error))
    },
  })
}

export function useDeleteSimulationNote(simulationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (noteId: string) =>
      simulationsApi.deleteNote(simulationId, noteId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: simulationKeys.notes(simulationId),
      })
      toast.success('Note deleted')
    },
    onError: (error) => {
      toast.error(getErrorMessage(error))
    },
  })
}
