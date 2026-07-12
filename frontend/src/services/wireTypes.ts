import type { components } from './generated/api';

type Schema<Name extends keyof components['schemas']> = components['schemas'][Name];

export type CGEMRunData = Schema<'CGEMRunData'>;
export type CGEMRunResponse = Schema<'CGEMRunResponse'>;
export type HealthResponse = Schema<'HealthResponse'>;
export type ManeuverDescriptors = Schema<'ManeuverDescriptors'>;
export type PilotConfigRequest = Schema<'PilotConfigRequest'>;
export type PredictionRequest = Schema<'PredictionRequest'>;
export type PredictionResponse = Schema<'PredictionResponse'>;
export type RunCGEMRequest = Schema<'RunCGEMRequest'>;
export type SensitivityResponse = Schema<'SensitivityResponse'>;
export type SobolFeatureIndex = Schema<'SobolFeatureIndex'>;
export type SweepRequest = Schema<'SweepRequest'>;
export type SweepResponse = Schema<'SweepResponse'>;
export type TargetPrediction = Schema<'TargetPrediction'>;
export type VersionResponse = Schema<'VersionResponse'>;
