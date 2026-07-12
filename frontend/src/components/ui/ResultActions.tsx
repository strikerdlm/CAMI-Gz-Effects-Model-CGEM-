import React, { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react';
import type { ExportSpec } from '../../services/exportResult';
interface ResultActionsValue { activeExport: ExportSpec | null; registerExport: (spec: ExportSpec | null) => void | (() => void) }
const noopRegisterExport = () => undefined;
const ResultActionsContext = createContext<ResultActionsValue>({ activeExport: null, registerExport: noopRegisterExport });
export function ResultActionsProvider({ children }: { children: React.ReactNode }) {
  const [activeExport, setActiveExport] = useState<ExportSpec | null>(null);
  const registrations = useRef(new Map<number, ExportSpec>());
  const nextId = useRef(0);
  const registerExport = useCallback((spec: ExportSpec | null) => {
    if (!spec) { registrations.current.clear(); setActiveExport(null); return; }
    const id = ++nextId.current; registrations.current.set(id, spec); setActiveExport(spec);
    return () => {
      registrations.current.delete(id);
      const remaining = Array.from(registrations.current.values());
      setActiveExport(remaining.at(-1) ?? null);
    };
  }, []);
  const value = useMemo(() => ({ activeExport, registerExport }), [activeExport, registerExport]);
  return <ResultActionsContext.Provider value={value}>{children}</ResultActionsContext.Provider>;
}
// eslint-disable-next-line react-refresh/only-export-components
export function useResultActions(): ResultActionsValue { return useContext(ResultActionsContext); }
