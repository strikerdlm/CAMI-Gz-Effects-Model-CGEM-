import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';
import type { ExportSpec } from '../../services/exportResult';
interface ResultActionsValue { activeExport: ExportSpec | null; registerExport: (spec: ExportSpec | null) => void }
const noopRegisterExport = () => undefined;
const ResultActionsContext = createContext<ResultActionsValue>({ activeExport: null, registerExport: noopRegisterExport });
export function ResultActionsProvider({ children }: { children: React.ReactNode }) { const [activeExport, setActiveExport] = useState<ExportSpec | null>(null); const registerExport = useCallback((spec: ExportSpec | null) => setActiveExport(spec), []); const value = useMemo(() => ({ activeExport, registerExport }), [activeExport, registerExport]); return <ResultActionsContext.Provider value={value}>{children}</ResultActionsContext.Provider>; }
// eslint-disable-next-line react-refresh/only-export-components
export function useResultActions(): ResultActionsValue { return useContext(ResultActionsContext); }
