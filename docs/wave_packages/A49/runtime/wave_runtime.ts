export interface WaveMetrics {
  wave: string;
  maturity: number;
  convergence: number;
  survivability: number;
  completion: number;
}

export interface RGLDomain {
  domain: string;
  maturity: number;
  global_completion: number;
  lineage_depth: number;
  iterations: number;
  seniority_rank: 'RGL-active' | 'RGL-senior' | 'RGL-elder';
}

export function weightedPriority(
  weakness: number,
  propagationGain: number,
  effort: number
): number {
  return (weakness * propagationGain) / Math.max(effort, 1);
}

export function describeRGL(): string {
  return 'RGL domains continue evolving while gaining recursive governance authority and convergence gravity.';
}
