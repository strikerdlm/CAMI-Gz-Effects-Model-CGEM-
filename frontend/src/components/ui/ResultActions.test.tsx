import { useEffect } from 'react';
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import type { ExportSpec } from '../../services/exportResult';
import { ResultActionsProvider, useResultActions } from './ResultActions';

const spec: ExportSpec = { filename: 'one.json', mediaType: 'application/json', content: '{}' };
function Registrar({ active }: { active: boolean }) { const { registerExport } = useResultActions(); useEffect(() => { registerExport(active ? spec : null); return () => registerExport(null); }, [active, registerExport]); return null; }
function Probe() { const { activeExport } = useResultActions(); return <output>{activeExport?.filename ?? 'none'}</output>; }

it('registers, replaces, and unregisters active result exports without stale content', () => {
  const view = render(<ResultActionsProvider><Registrar active /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('one.json')).toBeInTheDocument();
  view.rerender(<ResultActionsProvider><Registrar active={false} /><Probe /></ResultActionsProvider>);
  expect(screen.getByText('none')).toBeInTheDocument();
  view.unmount();
});
