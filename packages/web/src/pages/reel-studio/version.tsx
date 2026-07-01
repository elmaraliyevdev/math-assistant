import { ConstraintStudioProvider } from '@/features/reel-studio/constraints/context/constraint-studio-context'
import { DesignStudioLayout } from '@/features/reel-studio/constraints/components/DesignStudioLayout'
import { GeneratorProvider } from '@/features/reel-studio/generator/context/generator-context'
import { OptimizerProvider } from '@/features/reel-studio/optimizer/context/optimizer-context'
import { ReelStudioProvider } from '@/features/reel-studio/context/reel-studio-context'
import { parseCanonicalJson } from '@/features/reel-studio/lib/parse-canonical'
import { useGame, useGameVersion } from '@/features/games/hooks/use-games'
import { Skeleton } from '@/components/ui/skeleton'
import { useParams } from '@tanstack/react-router'
import { useMemo } from 'react'

export function ReelStudioVersionPage() {
  const { gameId, versionId } = useParams({ strict: false }) as {
    gameId: string
    versionId: string
  }
  const game = useGame(gameId)
  const version = useGameVersion(gameId, versionId)

  const document = useMemo(() => {
    if (!version.data) {
      return null
    }
    return parseCanonicalJson(version.data.canonicalJson, version.data.engineVersion)
  }, [version.data])

  if (game.isLoading || version.isLoading) {
    return <Skeleton className="h-full w-full" />
  }

  if (!game.data || !version.data || !document) {
    return <p className="text-muted-foreground">Version not found.</p>
  }

  return (
    <ReelStudioProvider key={versionId} initialDocument={document}>
      <ConstraintStudioProvider>
        <GeneratorProvider>
          <OptimizerProvider>
            <DesignStudioLayout
              gameId={gameId}
              versionId={versionId}
              gameName={game.data.name}
              versionNumber={version.data.version}
            />
          </OptimizerProvider>
        </GeneratorProvider>
      </ConstraintStudioProvider>
    </ReelStudioProvider>
  )
}
