import { readFile } from 'node:fs/promises';

export const TURN_DEFINITION =
  'A turn is one turn_start through turn_end pair when markers exist; logs without markers use one user prompt plus following assistant/tool rows.';

function textFromContent(content) {
  if (!Array.isArray(content)) return '';
  return content
    .filter((part) => part && part.type === 'text')
    .map((part) => part.text ?? '')
    .join('\n');
}

function pushTurn(turns, current) {
  if (current) turns.push(current);
}

const USAGE_TOKEN_FIELDS = ['input', 'output', 'cacheRead', 'cacheWrite'];

function assertUsageTokens(assistants, turnIndex, source) {
  for (const message of assistants) {
    const usage = message.usage ?? {};
    if (usage === null || typeof usage !== 'object') continue;
    for (const field of USAGE_TOKEN_FIELDS) {
      const value = usage[field];
      if (value === undefined || value === null) continue;
      if (typeof value === 'boolean' || !Number.isFinite(Number(value)) || Number(value) < 0) {
        const error = new Error(`invalid usage tokens in ${source} turn ${turnIndex}: ${field}=${JSON.stringify(value)} (must be a non-negative number)`);
        error.code = 'INVALID_USAGE_TOKENS';
        throw error;
      }
    }
    const total = usage.cost?.total;
    if (total !== undefined && total !== null && (typeof total === 'boolean' || !Number.isFinite(Number(total)) || Number(total) < 0)) {
      const error = new Error(`invalid usage tokens in ${source} turn ${turnIndex}: cost.total=${JSON.stringify(total)} (must be a non-negative number)`);
      error.code = 'INVALID_USAGE_TOKENS';
      throw error;
    }
  }
}

function finishTurn(current, source = '<memory>') {
  assertUsageTokens(current.assistants, current.turnIndex, source);
  const assistants = current.assistants;
  const models = [...new Set(assistants.map((message) => message.model ?? message.activeModel).filter(Boolean))];
  const usage = assistants.map((message) => message.usage).filter(Boolean);
  const costs = usage.map((value) => value.cost).filter(Boolean);
  const promptTokens = usage.length
    ? usage.reduce((total, value) => total + (Number(value.input) || 0), 0)
    : null;
  const completionTokens = usage.length
    ? usage.reduce((total, value) => total + (Number(value.output) || 0), 0)
    : null;
  const actualSpend = costs.length
    ? costs.reduce((total, value) => total + (Number(value.total) || 0), 0)
    : null;
  const toolCalls = assistants.reduce(
    (total, message) => total + (message.content ?? []).filter((part) => part?.type === 'toolCall').length,
    0,
  );
  let skipReason = null;
  if (assistants.length === 0) skipReason = 'no assistant response';
  else if (models.length === 0) skipReason = 'served model not recorded';
  return {
    sessionId: current.sessionId,
    turnIndex: current.turnIndex,
    model: models.length === 1 ? models[0] : models,
    models,
    promptTokens,
    completionTokens,
    actualSpend,
    toolCalls,
    assistantMessages: assistants.length,
    classifiable: skipReason === null,
    skipReason,
  };
}

export function parseSessionText(text, source = '<memory>') {
  const rows = text.split(/\r?\n/).filter((line) => line.trim());
  let sessionId = null;
  let activeModel = null;
  let turnIndex = 0;
  let current = null;
  let markerMode = false;
  const turns = [];

  for (const [lineIndex, line] of rows.entries()) {
    let row;
    try {
      row = JSON.parse(line);
    } catch (error) {
      const malformed = new Error(`invalid JSON in ${source} at nonblank line ${lineIndex + 1}: ${error.message}`);
      malformed.code = 'MALFORMED_JSONL';
      throw malformed;
    }
    if (row.type === 'session') {
      const id = row.id ?? row.sessionId ?? sessionId;
      if (id !== null && id !== undefined && typeof id !== 'string') {
        const badId = new Error(`non-string session id in ${source} at nonblank line ${lineIndex + 1}: ${JSON.stringify(id)}`);
        badId.code = 'NON_STRING_SESSION_ID';
        throw badId;
      }
      sessionId = id;
      continue;
    }
    if (row.type === 'model_change') {
      activeModel = row.model ?? activeModel;
      continue;
    }
    if (row.type === 'turn_start') {
      markerMode = true;
      pushTurn(turns, current);
      turnIndex += 1;
      current = { sessionId, turnIndex, user: null, assistants: [] };
      continue;
    }
    if (row.type === 'turn_end') {
      pushTurn(turns, current);
      current = null;
      continue;
    }
    if ((row.type !== 'message' && row.type !== 'message_end') || !row.message) continue;
    const message = row.message;
    if (message.role === 'user') {
      if (!current || (!markerMode && current.user)) {
        pushTurn(turns, current);
        turnIndex += 1;
        current = { sessionId, turnIndex, user: message, assistants: [] };
      } else if (!current.user) {
        current.user = message;
      } else {
        current.user = {
          ...current.user,
          content: [...(current.user.content ?? []), ...(message.content ?? [])],
        };
      }
    } else if (message.role === 'assistant') {
      if (!current) {
        turnIndex += 1;
        current = { sessionId, turnIndex, user: null, assistants: [] };
      }
      current.assistants.push({ ...message, activeModel });
    }
  }
  pushTurn(turns, current);
  const normalized = turns.map((turn) => finishTurn(turn, source));
  const classifiableTurns = normalized.filter((turn) => turn.classifiable).length;
  const skippedTurns = normalized.length - classifiableTurns;
  return {
    source,
    sessionId,
    rows: rows.length,
    turns: normalized,
    totals: {
      turns: normalized.length,
      classifiableTurns,
      skippedTurns,
    },
  };
}

export function requireClassifiable(result) {
  if (result.totals.classifiableTurns === 0) {
    const error = new Error('no classifiable turns found in supplied session logs');
    error.code = 'EMPTY_CLASSIFIABLE_SET';
    throw error;
  }
  return result;
}

export async function readSessionLog(path) {
  return parseSessionText(await readFile(path, 'utf8'), path);
}

export async function readSessionLogs(paths) {
  const sessions = await Promise.all(paths.map(readSessionLog));
  const seen = new Map();
  for (const session of sessions) {
    const id = session.sessionId;
    if (id === null || id === undefined) continue;
    if (seen.has(id)) {
      const error = new Error(`duplicate session id ${JSON.stringify(id)} in ${seen.get(id)} and ${session.source} (same session counted twice inflates the denominator)`);
      error.code = 'DUPLICATE_SESSION_ID';
      throw error;
    }
    seen.set(id, session.source);
  }
  const turns = sessions.flatMap((session) => session.turns);
  const classifiableTurns = turns.filter((turn) => turn.classifiable).length;
  return requireClassifiable({
    sessions,
    turns,
    totals: {
      sessions: sessions.length,
      turns: turns.length,
      classifiableTurns,
      skippedTurns: turns.length - classifiableTurns,
    },
  });
}
