const finiteProbability = (value) => Number.isFinite(value) && value >= 0 && value <= 1;

function refuse(reason) {
  return { status: 'REFUSE', reason };
}

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function betaBinomialRatio(n, a, b, k) {
  return ((n - k) * (k + a)) / ((k + 1) * (n - k - 1 + b));
}

function centralBetaBinomialInterval(nCalibration, nTest, alpha) {
  const l = Math.floor((nCalibration + 1) * alpha);
  const a = nCalibration + 1 - l;
  const b = l;
  if (b === 0) {
    return { lowerCount: nTest, upperCount: nTest, confidence: 0.95 };
  }

  let mode = 0;
  for (let k = 0; k < nTest; k++) {
    if (betaBinomialRatio(nTest, a, b, k) < 1) break;
    mode = k + 1;
  }
  const weights = new Float64Array(nTest + 1);
  weights[mode] = 1;
  for (let k = mode; k < nTest; k++) {
    weights[k + 1] = weights[k] * betaBinomialRatio(nTest, a, b, k);
  }
  for (let k = mode - 1; k >= 0; k--) {
    weights[k] = weights[k + 1] / betaBinomialRatio(nTest, a, b, k);
  }
  let total = 0;
  for (const weight of weights) total += weight;
  if (!Number.isFinite(total) || total <= 0) {
    throw new Error('beta-binomial normalization failed');
  }
  const quantile = (target) => {
    let cumulative = 0;
    for (let k = 0; k <= nTest; k++) {
      cumulative += weights[k] / total;
      if (cumulative >= target) return k;
    }
    return nTest;
  };
  return {
    lowerCount: quantile(0.025),
    upperCount: quantile(0.975),
    confidence: 0.95,
  };
}

function validFrame(frame) {
  if (!isRecord(frame)
      || typeof frame.name !== 'string' || !frame.name.trim()
      || typeof frame.source !== 'string' || !frame.source.trim()
      || typeof frame.targetPopulation !== 'string' || !frame.targetPopulation.trim()
      || !isRecord(frame.calibrationGroup) || !isRecord(frame.testGroup)) {
    return false;
  }
  const calibration = frame.calibrationGroup;
  const test = frame.testGroup;
  return typeof calibration.name === 'string' && Boolean(calibration.name.trim())
    && typeof test.name === 'string' && Boolean(test.name.trim())
    && calibration.name !== test.name
    && calibration.targetPopulation === frame.targetPopulation
    && test.targetPopulation === frame.targetPopulation;
}

function validateRows(rows, group, frame, labels, ids) {
  if (!Array.isArray(rows) || rows.length === 0) return { reason: 'empty_split' };
  const scores = [];
  for (const row of rows) {
    if (!isRecord(row)
        || (typeof row.id !== 'string' && !(typeof row.id === 'number' && Number.isFinite(row.id)))
        || row.samplingFrame !== frame.name
        || row.group !== group.name
        || typeof row.trueLabel !== 'string'
        || !labels.has(row.trueLabel)) {
      return { reason: 'row_outside_named_sampling_frame' };
    }
    const id = `${typeof row.id}:${row.id}`;
    if (ids.has(id)) return { reason: 'duplicate_split_id' };
    ids.add(id);

    if (!isRecord(row.probabilities)) return { reason: 'invalid_probability_vector' };
    const keys = Object.keys(row.probabilities);
    if (keys.length !== labels.size || keys.some((label) => !labels.has(label))) {
      return { reason: 'invalid_probability_vector' };
    }
    let total = 0;
    for (const label of labels) {
      const value = row.probabilities[label];
      if (!finiteProbability(value)) return { reason: 'invalid_probability_vector' };
      total += value;
    }
    if (!Number.isFinite(total) || Math.abs(total - 1) > 1e-6) {
      return { reason: 'invalid_probability_vector' };
    }
    const probability = Math.max(row.probabilities[row.trueLabel], row.probabilityFloor ?? 0.005);
    scores.push({ id: row.id, trueLabel: row.trueLabel, score: 1 - probability, probabilities: row.probabilities });
  }
  return { scores };
}

/**
 * Split-conformal LAC for a predeclared, disjoint calibration/test split.
 * The returned set uses the finite-sample order statistic; ties at q-hat are included.
 */
export function splitConformalLac(input) {
  if (!isRecord(input)) return refuse('invalid_input');
  const { calibration, test, labels, alpha, samplingFrame } = input;
  const floor = input.probabilityFloor ?? 0.005;
  if (!Array.isArray(labels) || labels.length === 0
      || labels.some((label) => typeof label !== 'string' || !label.trim())
      || new Set(labels).size !== labels.length) {
    return refuse('invalid_labels');
  }
  if (!finiteProbability(alpha) || alpha === 0 || alpha === 1) return refuse('invalid_alpha');
  if (!finiteProbability(floor)) return refuse('invalid_probability_floor');
  if (!validFrame(samplingFrame)) return refuse('named_sampling_frame_required');
  if (!Array.isArray(calibration) || !Array.isArray(test)
      || calibration.length === 0 || test.length === 0) return refuse('empty_split');

  const labelSet = new Set(labels);
  const calibrationIds = new Set();
  const calibrationResult = validateRows(
    calibration, samplingFrame.calibrationGroup, samplingFrame, labelSet, calibrationIds,
  );
  if (calibrationResult.reason) return refuse(calibrationResult.reason);
  const testIds = new Set();
  const testResult = validateRows(test, samplingFrame.testGroup, samplingFrame, labelSet, testIds);
  if (testResult.reason) return refuse(testResult.reason);
  for (const id of testIds) {
    if (calibrationIds.has(id)) return refuse('overlapping_split_ids');
  }

  const rank = Math.ceil((calibration.length + 1) * (1 - alpha));
  const scores = calibrationResult.scores.map((item) => item.score).sort((a, b) => a - b);
  const threshold = rank > scores.length ? Number.POSITIVE_INFINITY : scores[rank - 1];
  const orderedLabels = [...labels].sort();
  const predictionSets = testResult.scores.map((item) => {
    const members = orderedLabels.filter((label) =>
      1 - Math.max(item.probabilities[label], floor) <= threshold);
    return { id: item.id, labels: members, covered: members.includes(item.trueLabel) };
  });
  let covered = 0;
  let totalSize = 0;
  let singletonCount = 0;
  for (const prediction of predictionSets) {
    if (prediction.covered) covered++;
    totalSize += prediction.labels.length;
    if (prediction.labels.length === 1) singletonCount++;
  }
  const nTest = test.length;
  const coverageBand = centralBetaBinomialInterval(calibration.length, nTest, alpha);
  return {
    status: 'OK',
    nCalibration: calibration.length,
    nTest,
    alpha,
    calibrationRank: rank,
    threshold,
    covered,
    coverage: covered / nTest,
    coverageBand,
    meanSetSize: totalSize / nTest,
    singletonShare: singletonCount / nTest,
    predictionSets,
  };
}
