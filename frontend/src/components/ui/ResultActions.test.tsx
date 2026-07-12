import { useEffect } from 'react';
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import type { ExportSpec } from '../../services/exportResult';
import { ResultActionsProvider, useResultActions } from './ResultActions';

const spec: ExportSpec = { filename: 'one.json', mediaType: 'application/json', content: '{}' };
function Registrar({ active }: { active: boolean }) { const { registerExport } = useResultActions(); useEffect(() => { const unregister = registerExport(active ? spec : null); return typeof unregister === 'function' ? unregister : undefined; }, [active, registerExport]); return null; }
function Probe() { const { activeExport } = useResultActions(); return <output>{activeExport?.filename ?? 'none'}</output>; }

it('registers, replaces, and unregisters active result exports without stale content', () => {
  const view = render(<ResultActionsProvider><Registrar active /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('one.json')).toBeInTheDocument();
  view.rerender(<ResultActionsProvider><Registrar active={false} /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('none')).toBeInTheDocument();
  view.unmount();
});

function NamedRegistrar({ spec: value }: { spec: ExportSpec }) { const { registerExport } = useResultActions(); useEffect(() => { const unregister = registerExport(value); return typeof unregister === 'function' ? unregister : undefined; }, [value, registerExport]); return null; }

it('replaces a non-null export and removes it when its registrar unmounts', () => {
  const two = { ...spec, filename: 'two.json' };
  const view = render(<ResultActionsProvider><NamedRegistrar spec={spec} /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('one.json')).toBeInTheDocument();
  view.rerender(<ResultActionsProvider><NamedRegistrar spec={two} /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('two.json')).toBeInTheDocument();
  view.rerender(<ResultActionsProvider><Probe /></ResultActionsProvider>);
  expect(screen.getByText('none')).toBeInTheDocument();
});

it('does not clear a competing active export when another registrar unmounts', () => {
  const two = { ...spec, filename: 'two.json' };
  const view = render(<ResultActionsProvider><NamedRegistrar spec={spec} /><NamedRegistrar spec={two} /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('two.json')).toBeInTheDocument();
  view.rerender(<ResultActionsProvider><NamedRegistrar spec={two} /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('two.json')).toBeInTheDocument();
});
