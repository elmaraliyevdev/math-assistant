import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { collaborationApi } from '@/features/collaboration/api/collaboration-api'

export const collaborationKeys = {
  workflow: (simulationId: string) =>
    ['collaboration', 'workflow', simulationId] as const,
  comments: (simulationId: string) =>
    ['collaboration', 'comments', simulationId] as const,
  activity: (simulationId: string) =>
    ['collaboration', 'activity', simulationId] as const,
}

export function useSimulationWorkflow(simulationId: string, enabled = true) {
  return useQuery({
    queryKey: collaborationKeys.workflow(simulationId),
    queryFn: () => collaborationApi.getWorkflow(simulationId),
    enabled: enabled && Boolean(simulationId),
  })
}

export function useSimulationComments(simulationId: string, enabled = true) {
  return useQuery({
    queryKey: collaborationKeys.comments(simulationId),
    queryFn: () => collaborationApi.listComments(simulationId),
    enabled: enabled && Boolean(simulationId),
  })
}

export function useSimulationActivity(simulationId: string, enabled = true) {
  return useQuery({
    queryKey: collaborationKeys.activity(simulationId),
    queryFn: () => collaborationApi.listActivity(simulationId),
    enabled: enabled && Boolean(simulationId),
  })
}

function invalidateCollaboration(
  queryClient: ReturnType<typeof useQueryClient>,
  simulationId: string,
) {
  void queryClient.invalidateQueries({
    queryKey: collaborationKeys.workflow(simulationId),
  })
  void queryClient.invalidateQueries({
    queryKey: collaborationKeys.comments(simulationId),
  })
  void queryClient.invalidateQueries({
    queryKey: collaborationKeys.activity(simulationId),
  })
}

export function useAddSimulationComment(simulationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (content: string) =>
      collaborationApi.addComment(simulationId, content),
    onSuccess: () => invalidateCollaboration(queryClient, simulationId),
  })
}

export function useSubmitSimulationReview(simulationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: { status: string; decisionReason?: string }) =>
      collaborationApi.submitReview(simulationId, payload),
    onSuccess: () => invalidateCollaboration(queryClient, simulationId),
  })
}

export function useApproveSimulation(simulationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (approvalStage: string) =>
      collaborationApi.approve(simulationId, approvalStage),
    onSuccess: () => invalidateCollaboration(queryClient, simulationId),
  })
}

export function useTransitionWorkflow(simulationId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (targetStatus: string) =>
      collaborationApi.transitionWorkflow(simulationId, targetStatus),
    onSuccess: () => invalidateCollaboration(queryClient, simulationId),
  })
}
