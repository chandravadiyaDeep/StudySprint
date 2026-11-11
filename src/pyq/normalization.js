/* Conservative text normalization. Preserve the raw question separately. */
(function (root) {
  "use strict";

  const STOP_WORDS = new Set([
    "the", "and", "for", "with", "from", "what", "when", "where", "which",
    "write", "explain", "define", "describe", "discuss", "using", "give",
    "show", "derive", "state"
  ]);

  function normalizeQuestion(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/\b(?:q(?:uestion)?\.?\s*)?\d{1,3}\b/g, " ")
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  function tokenSet(value) {
    return new Set(
      normalizeQuestion(value)
        .split(" ")
        .filter((token) => token.length > 2 && !STOP_WORDS.has(token))
    );
  }

  root.StudySprintPYQ = root.StudySprintPYQ || {};
  root.StudySprintPYQ.normalizeQuestion = normalizeQuestion;
  root.StudySprintPYQ.tokenSet = tokenSet;
})(typeof globalThis !== "undefined" ? globalThis : window);
