export const registeredAdapters = [
  {
    id: "jev-recorded",
    modelId: "jev-1.13.0",
    probabilities: "required",
    usesTransport: true,
    async evaluate(request, transport) {
      return transport({ ...request, backendId: "jev-recorded" });
    },
  },
  {
    id: "regex-rule",
    modelId: "regex-rule",
    probabilities: "unsupported",
    usesTransport: false,
    async evaluate({ question }) {
      const entry = Object.entries(question.options ?? {}).find(([, option]) => option.action === "pass");
      if (!entry) throw new TypeError("rule adapter has no pass option");
      return { choice: entry[0], modelId: "regex-rule", costUsd: 0 };
    },
  },
];
