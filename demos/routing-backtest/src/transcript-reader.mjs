import { readFile } from 'node:fs/promises';

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

function finishTurn(current) {
  const userText = textFromContent(current.user.content);
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
  if (!userText.trim()) skipReason = 'empty user prompt';
  else if (assistants.length === 0) skipReason = 'no assistant response';
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
  const turns = [];

  for (const [lineIndex, line] of rows.entries()) {
    let row;
    try {
      row = JSON.parse(line);
    } catch (error) {
      throw new Error(`invalid JSON in ${source} at nonblank line ${lineIndex + 1}: ${error.message}`);
    }
    if (row.type === 'session') {
      sessionId = row.id ?? sessionId;
      continue;
    }
    if (row.type === 'model_change') {
      activeModel = row.model ?? activeModel;
      continue;
    }
    if ((row.type !== 'message' && row.type !== 'message_end') || !row.message) continue;
    const message = row.message;
    if (message.role === 'user') {
      pushTurn(turns, current);
      turnIndex += 1;
      current = { sessionId, turnIndex, user: message, assistants: [] };
    } else if (message.role === 'assistant' && current) {
      current.assistants.push({ ...message, activeModel });
    }
  }
  pushTurn(turns, current);
  const normalized = turns.map(finishTurn);
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
