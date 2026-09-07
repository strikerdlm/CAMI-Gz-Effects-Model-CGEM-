import { lazy, Suspense } from "react";
import { useSearchParams } from "react-router-dom";

const FlightLab = lazy(() => import("../features/flight/FlightLab"));
const TraceLesson = lazy(() => import("../features/flight/TraceLesson"));

export function SimulatorPage() {
  const [params] = useSearchParams();
  const trace = params.has("id") || params.get("mode") === "trace";
  return (
    <Suspense
      fallback={
        <div className="p-8 text-hud-ink">Loading the learning lab…</div>
      }
    >
      {trace ? <TraceLesson /> : <FlightLab />}
    </Suspense>
  );
}
