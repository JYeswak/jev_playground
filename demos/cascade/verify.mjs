/**
 * Fixture SDE cascade (cookbook shape, FIXTURE SCORING).
 * A cheap extraction produces a schema-valid record that is still wrong;
 * a per-field Noul battery (true = escalate) checks each field, and any
 * head at or above THRESHOLD escalates the record. The holistic overall
 * head is computed and displayed but never drives the gate.
 * Fixture Nouls stand in for the verify call.
 */
export const THRESHOLD = 0.5;

export const FIELDS = [
  { path: "title", spec: "event title", value: "Mobile Navigation", p_wrong: 0.08 },
  { path: "registration_open_date", spec: "date registration opens", value: "", p_wrong: 0.12 },
  { path: "location", spec: "venue city", value: "Cupertino", p_wrong: 0.71 },
];

export function verify(fields = FIELDS) {
  const heads = fields.map((f) => ({
    field: f.path,
    question: `Is the extracted ${f.path} wrong against its spec (${f.spec})?`,
    p: f.value === "" ? 0.12 : f.p_wrong,
  }));
  const overall = Math.max(...heads.map((h) => h.p));
  const escalations = heads.filter((h) => h.p >= THRESHOLD);
  return { heads, overall, escalate: escalations.length > 0, escalations: escalations.map((h) => h.field) };
}
