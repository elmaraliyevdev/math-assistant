import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  SettingSwitchRow,
  SettingsFieldGroup,
  SettingsSectionHeader,
} from '@/features/settings/components/settings-primitives'
import { useUpdatePreferences } from '@/features/settings/hooks/use-settings'
import { useThemeStore, type ThemePreference } from '@/stores/theme-store'
import {
  useUiPreferencesStore,
  type ChartTheme,
  type CodeFont,
  type UiAccent,
  type UiDensity,
} from '@/stores/ui-preferences-store'

export function AppearanceSection() {
  const theme = useThemeStore((state) => state.theme)
  const setTheme = useThemeStore((state) => state.setTheme)
  const updatePreferences = useUpdatePreferences()

  const density = useUiPreferencesStore((state) => state.density)
  const accent = useUiPreferencesStore((state) => state.accent)
  const animations = useUiPreferencesStore((state) => state.animations)
  const sidebarCollapsed = useUiPreferencesStore((state) => state.sidebarCollapsed)
  const codeFont = useUiPreferencesStore((state) => state.codeFont)
  const chartTheme = useUiPreferencesStore((state) => state.chartTheme)
  const setDensity = useUiPreferencesStore((state) => state.setDensity)
  const setAccent = useUiPreferencesStore((state) => state.setAccent)
  const setAnimations = useUiPreferencesStore((state) => state.setAnimations)
  const setSidebarCollapsed = useUiPreferencesStore((state) => state.setSidebarCollapsed)
  const setCodeFont = useUiPreferencesStore((state) => state.setCodeFont)
  const setChartTheme = useUiPreferencesStore((state) => state.setChartTheme)

  return (
    <div className="space-y-5">
      <SettingsSectionHeader
        title="Appearance"
        description="Customize how the workspace looks and feels."
      />

      <SettingsFieldGroup title="Theme">
        <Select
          value={theme}
          onValueChange={(value) => {
            const preference = value as ThemePreference
            setTheme(preference)
            if (preference === 'light' || preference === 'dark') {
              updatePreferences.mutate({ theme: preference })
            }
          }}
        >
          <SelectTrigger className="max-w-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="light">Light</SelectItem>
            <SelectItem value="dark">Dark</SelectItem>
            <SelectItem value="system">System</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Accent color">
        <Select value={accent} onValueChange={(value) => setAccent(value as UiAccent)}>
          <SelectTrigger className="max-w-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="blue">Blue</SelectItem>
            <SelectItem value="violet">Violet</SelectItem>
            <SelectItem value="emerald">Emerald</SelectItem>
            <SelectItem value="amber">Amber</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Density">
        <Select value={density} onValueChange={(value) => setDensity(value as UiDensity)}>
          <SelectTrigger className="max-w-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="compact">Compact</SelectItem>
            <SelectItem value="comfortable">Comfortable</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Interface">
        <div className="space-y-2">
          <SettingSwitchRow
            label="Animations"
            description="Enable motion for panels, charts, and transitions."
            checked={animations}
            onCheckedChange={setAnimations}
          />
          <SettingSwitchRow
            label="Sidebar collapsed by default"
            description="Start with the navigation sidebar minimized."
            checked={sidebarCollapsed}
            onCheckedChange={setSidebarCollapsed}
          />
        </div>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Code font">
        <Select value={codeFont} onValueChange={(value) => setCodeFont(value as CodeFont)}>
          <SelectTrigger className="max-w-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="jetbrains">JetBrains Mono</SelectItem>
            <SelectItem value="fira">Fira Code</SelectItem>
            <SelectItem value="system">System monospace</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldGroup>

      <SettingsFieldGroup title="Chart theme">
        <Select
          value={chartTheme}
          onValueChange={(value) => setChartTheme(value as ChartTheme)}
        >
          <SelectTrigger className="max-w-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="default">Default</SelectItem>
            <SelectItem value="muted">Muted</SelectItem>
            <SelectItem value="high-contrast">High contrast</SelectItem>
          </SelectContent>
        </Select>
      </SettingsFieldGroup>
    </div>
  )
}
