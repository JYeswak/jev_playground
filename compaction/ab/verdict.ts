export type SamplingSummary = {
  deterministic: boolean;
  determinism: 'established' | 'unestablished';
  sampleCount: number;
  scores: number[];
  min: number;
  max: number;
  spread: number;
};

export function summarizeSamples(scores: number[], deterministicClaim = false): SamplingSummary {
  if (scores.length === 0) {
    throw new Error('sampling requires at least one score');
  }
  const min = Math.min(...scores);
  const max = Math.max(...scores);
  const spread = max - min;
  const established = scores.length >= 10 && spread === 0;
  return {
    deterministic: deterministicClaim && established,
    determinism: established ? 'established' : 'unestablished',
    sampleCount: scores.length,
    scores,
    min,
    max,
    spread,
  };
}

export function requestedVerdict(
  armA: SamplingSummary,
  armB: SamplingSummary,
): 'A wins' | 'B wins' | 'tie' {
  if (armA.determinism !== 'established' || armB.determinism !== 'established') {
    throw new Error(
      `verdict requires >=10 zero-spread samples per arm; armA n=${armA.sampleCount} spread=${armA.spread}, armB n=${armB.sampleCount} spread=${armB.spread}`,
    );
  }
  if (armA.min > armB.min) return 'A wins';
  if (armB.min > armA.min) return 'B wins';
  return 'tie';
}
