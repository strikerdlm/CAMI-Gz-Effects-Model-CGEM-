/**
 * Settings — /settings
 * Persists to localStorage via `state/useUserPrefs.ts`.
 * Editing the API URL takes effect immediately (axios interceptor reads
 * prefs at request time, no reload required).
 */
import React, { useState } from 'react';
import { Bezel, SegmentReadout } from '../components/hud';
import {
  useUserPrefs,
  updateUserPrefs,
  DEFAULT_PREFS,
  type UserPrefs,
} from '../state/useUserPrefs';
import { useHealth, useVersion } from '../services/cgemApi';

type DefaultsKey = keyof UserPrefs['defaults'];

const DEFAULTS_FIELDS: readonly DefaultsKey[] = [
  'who_profile',
  'gsuit_max_psi',
  'gsuit_coverage_fraction',
  'agsm_effectiveness',
  'pbg_max_mmhg',
  'dehydration_level',
] as const;

export const SettingsPage: React.FC = () => {
  const prefs = useUserPrefs();
  const [apiUrlDraft, setApiUrlDraft] = useState(prefs.apiUrl);
  const health = useHealth();
  const version = useVersion();

  const applyApiUrl = (): void => {
    const cleaned = apiUrlDraft.trim().replace(/\/$/, '');
    if (cleaned.length === 0) return;
    updateUserPrefs({ apiUrl: cleaned });
    health.refetch();
    version.refetch();
  };

  const resetApiUrl = (): void => {
    setApiUrlDraft(DEFAULT_PREFS.apiUrl);
    updateUserPrefs({ apiUrl: DEFAULT_PREFS.apiUrl });
  };

  const updateDefault = (key: DefaultsKey, value: number): void => {
    if (!Number.isFinite(value)) return;
    updateUserPrefs({ defaults: { ...prefs.defaults, [key]: value } });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Bezel
        label="API CONNECTION"
        status={health.data?.status === 'ok' ? 'ok' : health.isError ? 'fail' : 'caution'}
      >
        <label className="block font-mono text-[10px] text-hud-ink-faint tracking-callsign uppercase">
          Base URL
        </label>
        <div className="flex gap-2 mt-1">
          <input
            type="text"
            value={apiUrlDraft}
            onChange={(e) => setApiUrlDraft(e.target.value)}
            spellCheck={false}
            className="flex-1 bg-hud-bg border border-hud-line text-hud-amber font-mono text-sm px-2 py-1 rounded-sm focus:outline-none focus:border-hud-amber"
          />
          <button
            onClick={applyApiUrl}
            className="px-3 py-1 bg-hud-amber/10 border border-hud-amber/50 text-hud-amber hover:bg-hud-amber/20 rounded-sm font-mono text-xs tracking-callsign uppercase"
          >
            Apply
          </button>
          <button
            onClick={resetApiUrl}
            className="px-3 py-1 bg-hud-panel border border-hud-line text-hud-ink-dim hover:text-hud-ink rounded-sm font-mono text-xs tracking-callsign uppercase"
          >
            Default
          </button>
        </div>
        <div className="mt-4 grid grid-cols-[120px_1fr] gap-x-4 gap-y-1.5 font-mono text-xs">
          <div className="text-hud-ink-faint">HEALTH</div>
          <div className={health.data?.status === 'ok' ? 'phosphor' : 'text-hud-red'}>
            {health.isPending ? '…' : health.data?.status ?? 'unknown'}
          </div>
          <div className="text-hud-ink-faint">PACKAGE</div>
          <div className="amber">{version.data?.package_version ?? '—'}</div>
          <div className="text-hud-ink-faint">BINARY</div>
          <div className="amber truncate">
            {version.data?.cgem_binary_sha256
              ? version.data.cgem_binary_sha256.slice(0, 16) + '…'
              : '—'}
          </div>
          <div className="text-hud-ink-faint">DATASET</div>
          <div className="amber">
            {version.data?.dataset_name ?? '—'} · seed {version.data?.dataset_master_seed ?? '—'}
          </div>
          <div className="text-hud-ink-faint">TARGETS</div>
          <div className="amber">{version.data?.targets?.length ?? 0}</div>
        </div>
      </Bezel>

      <Bezel label="DEFAULT PILOT CONFIG" status="ok">
        <div className="space-y-1">
          {DEFAULTS_FIELDS.map((k) => (
            <div
              key={k}
              className="flex items-center justify-between py-1 border-b border-hud-line/40 last:border-0"
            >
              <label className="font-mono text-[11px] text-hud-ink-faint tracking-callsign uppercase">
                {k.replace(/_/g, ' ')}
              </label>
              <input
                type="number"
                step={k === 'who_profile' ? 1 : 0.05}
                value={prefs.defaults[k]}
                onChange={(e) => updateDefault(k, Number(e.target.value))}
                className="w-28 bg-hud-bg border border-hud-line text-hud-amber font-mono text-sm px-2 py-0.5 rounded-sm text-right tabular-nums focus:outline-none focus:border-hud-amber"
              />
            </div>
          ))}
        </div>
        <p className="mt-3 text-hud-ink-faint font-mono text-[11px] leading-relaxed">
          These values seed every <span className="phosphor">/predict</span> and{' '}
          <span className="phosphor">/run-cgem</span> request from the Simulator and Dashboard
          unless overridden inline.
        </p>
      </Bezel>

      <Bezel label="DISPLAY" status="idle">
        <div className="space-y-3 font-mono text-xs">
          <div>
            <div className="text-hud-ink-faint tracking-callsign uppercase mb-1">
              Phosphor primary
            </div>
            <div className="flex gap-2">
              {(['amber', 'green'] as const).map((c) => (
                <button
                  key={c}
                  onClick={() => updateUserPrefs({ phosphorColor: c })}
                  className={
                    'px-3 py-1 rounded-sm border tracking-callsign uppercase ' +
                    (prefs.phosphorColor === c
                      ? c === 'amber'
                        ? 'bg-hud-amber/20 border-hud-amber text-hud-amber shadow-hud-glow-amber'
                        : 'bg-hud-phosphor/20 border-hud-phosphor text-hud-phosphor shadow-hud-glow-green'
                      : 'bg-hud-panel border-hud-line text-hud-ink-faint hover:text-hud-ink')
                  }
                >
                  {c}
                </button>
              ))}
            </div>
            <p className="mt-1 text-hud-ink-faint text-[10px]">
              Cosmetic preference recorded for future themes; current build pins the amber HUD.
            </p>
          </div>
          <div>
            <div className="text-hud-ink-faint tracking-callsign uppercase mb-1">
              Acceleration units
            </div>
            <div className="flex gap-2">
              {(['G', 'm_per_s2'] as const).map((u) => (
                <button
                  key={u}
                  onClick={() => updateUserPrefs({ units: u })}
                  className={
                    'px-3 py-1 rounded-sm border tracking-callsign uppercase ' +
                    (prefs.units === u
                      ? 'bg-hud-phosphor/20 border-hud-phosphor text-hud-phosphor'
                      : 'bg-hud-panel border-hud-line text-hud-ink-faint hover:text-hud-ink')
                  }
                >
                  {u === 'G' ? '+Gz' : 'm/s²'}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Bezel>

      <Bezel label="ABOUT" status="ok">
        <div className="font-mono text-xs text-hud-ink-dim space-y-2">
          <div className="font-condensed text-base text-hud-ink tracking-wide uppercase">
            CGEM · G-Effects Tactical Display
          </div>
          <div>FAA CAMI G-Effects Model · additive ML/UQ wrapper</div>
          <div className="pt-2">
            Frontend build:{' '}
            <SegmentReadout
              value={version.data?.package_version ?? '0.0.0'}
              tone="amber"
              size="sm"
            />
          </div>
          <a
            href="https://github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-"
            target="_blank"
            rel="noreferrer"
            className="phosphor hover:underline block pt-2"
          >
            github.com/strikerdlm/CAMI-Gz-Effects-Model-CGEM-
          </a>
          <div className="pt-2 text-hud-ink-faint text-[11px] leading-relaxed">
            FAA CAMI CGEM Fortran source DOI{' '}
            <a
              href="https://doi.org/10.21949/1524446"
              target="_blank"
              rel="noreferrer"
              className="amber hover:underline"
            >
              10.21949/1524446
            </a>
            . Frontend wraps the validated core; the binary is unmodified.
          </div>
        </div>
      </Bezel>
    </div>
  );
};
