const finiteRate = (value) => Number.isFinite(value) && value >= 0 && value <= 1;

function refuse(reason) {
  return { status: 'NOT_RUN', reason };
}

export function ppvAtPrevalence(sensitivity, falsePositiveRate, prevalence) {
  if (![sensitivity, falsePositiveRate, prevalence].every(finiteRate)) {
    return { status: 'UNKNOWN', reason: 'rates and prevalence must be finite probabilities' };
  }
  const truePositiveMass = sensitivity * prevalence;
  const falsePositiveMass = falsePositiveRate * (1 - prevalence);
  const predictedPositiveMass = truePositiveMass + falsePositiveMass;
  if (predictedPositiveMass === 0) return { status: 'UNKNOWN', reason: 'no predicted positives' };
  return { status: 'PROJECTED', ppv: truePositiveMass / predictedPositiveMass };
}

export function costCut({ sensitivity, falsePositiveRate, devPrevalence, deploymentPrevalence, costMatrix, positiveCount, negativeCount }) {
  if (!costMatrix || !Number.isFinite(costMatrix.falsePositive) || !Number.isFinite(costMatrix.falseNegative) || costMatrix.falsePositive < 0 || costMatrix.falseNegative < 0 || costMatrix.falsePositive + costMatrix.falseNegative === 0) return refuse('missing or invalid cost matrix');
  if (!Number.isInteger(positiveCount) || positiveCount < 1 || !Number.isInteger(negativeCount) || negativeCount < 1) return refuse('class counts required');
  if (![sensitivity, falsePositiveRate, devPrevalence, deploymentPrevalence].every(finiteRate) || devPrevalence === 0 || devPrevalence === 1) return refuse('rates and non-degenerate prevalences required');
  // Prior-shift odds update: preserve class-conditional likelihood ratio.
  const ratio = (deploymentPrevalence / (1 - deploymentPrevalence)) / (devPrevalence / (1 - devPrevalence));
  const threshold = costMatrix.falsePositive / (costMatrix.falsePositive + costMatrix.falseNegative);
  return { status: 'READY', threshold, priorOddsMultiplier: ratio, sensitivity, falsePositiveRate, devPrevalence, deploymentPrevalence, positiveCount, negativeCount };
}

export function npZeroErrorBound({ alpha, delta = 0.05, negatives, independent = false }) {
  if (!finiteRate(alpha) || alpha <= 0 || alpha >= 1 || !finiteRate(delta) || delta <= 0 || delta >= 1) return refuse('alpha and delta must be probabilities strictly between zero and one');
  if (!independent) return refuse('independent audit observations not established');
  if (!Number.isInteger(negatives?.fit) || negatives.fit < 1 || !Number.isInteger(negatives?.audit) || negatives.audit < 0) return refuse('separate fit and audit negative counts required');
  const requiredAudit = Math.ceil(Math.log(delta) / Math.log1p(-alpha));
  if (negatives.audit < requiredAudit) return refuse(`need ${requiredAudit} independent audit negatives; have ${negatives.audit}`);
  return { status: 'READY', requiredAudit, fitNegatives: negatives.fit, auditNegatives: negatives.audit, alpha, confidence: 1 - delta, maxObservedExceedances: 0, errorDirection: 'upper bound on false-positive rate' };
}

export function ppvReplay({ sensitivity, falsePositiveRate, prevalence, observedPpv }) {
  const projection = ppvAtPrevalence(sensitivity, falsePositiveRate, prevalence);
  if (projection.status !== 'PROJECTED' || !finiteRate(observedPpv)) return { status: 'UNKNOWN', reason: 'projection or observed precision unavailable' };
  return { status: Math.abs(projection.ppv - observedPpv) <= 0.01 ? 'PASS' : 'ASSUMPTION-VIOLATED', projectedPpv: projection.ppv, observedPpv, absoluteError: Math.abs(projection.ppv - observedPpv) };
}
