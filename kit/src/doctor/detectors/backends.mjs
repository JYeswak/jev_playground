const CLEF_HEALTH = 'http://127.0.0.1:11300/healthz';
const manual = { action: 'manual', reason: 'Restore the localbench gateway that serves the configured Clef route.' };

function routesToClef(inventory) {
  if (!Array.isArray(inventory?.surfaces)) return false;
  return inventory.surfaces.some((surface) => {
    const value = [surface?.how, surface?.model, surface?.backend, surface?.provider].filter((item) => typeof item === 'string').join(' ');
    return value.toLowerCase().includes('clef');
  });
}

export const detectors = [
  {
    id: 'fm-clef-unreachable', subsystem: 'local_backends', tier: 'Q', repo_required: false,
    data_sources: [CLEF_HEALTH],
    async run(ctx) {
      if (typeof ctx.fetch !== 'function') return [];
      const routed = routesToClef(ctx.inventory);
      let response;
      try {
        response = await ctx.fetch(CLEF_HEALTH, { method: 'GET', signal: AbortSignal.timeout(500) });
      } catch {
        return [{
          severity: routed ? 'P1' : 'P3', kind: 'E', title: 'Clef gateway is unreachable',
          evidence: { endpoint: CLEF_HEALTH, reachable: false, routed },
          remediation: manual,
        }];
      }
      const reachable = response?.ok === true || (Number.isInteger(response?.status) && response.status >= 200 && response.status < 300);
      if (reachable) return [];
      return [{
        severity: routed ? 'P1' : 'P3', kind: 'E', title: 'Clef gateway is unreachable',
        evidence: { endpoint: CLEF_HEALTH, reachable: false, routed },
        remediation: manual,
      }];
    },
  },
];
