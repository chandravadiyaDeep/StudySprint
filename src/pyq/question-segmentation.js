/* Question segmentation baseline. Keep raw text and question order for traceability. */
(function (root) {
  "use strict";

  function splitQuestions(text) {
    // Normalize line endings but do not rewrite the original question text stored below.
    const cleaned = String(text || "").replace(/\r/g, "").replace(/[ \t]+/g, " ").trim();
    if (!cleaned) return [];

    // Prefer explicit question numbering; paragraph fallback is deliberately marked weak.
    const numbered = cleaned
      .split(/(?=(?:^|\n)\s*(?:Q(?:uestion)?\.?\s*)?\d{1,3}\s*[).:\-])/im)
      .map((value) => value.trim())
      .filter(Boolean);

    const candidates = numbered.length > 1
      ? numbered
      : cleaned.split(/\n{1,}/).map((value) => value.trim()).filter((value) => value.length >= 35);

    return candidates
      .map((raw, index) => ({
        raw: raw.slice(0, 1800),
        sequence: index + 1,
        segmentationMethod: numbered.length > 1 ? "numbered-boundary" : "paragraph-fallback"
      }))
      .filter((question) => question.raw.length >= 18);
  }

  root.StudySprintPYQ = root.StudySprintPYQ || {};
  root.StudySprintPYQ.splitQuestions = splitQuestions;
})(typeof globalThis !== "undefined" ? globalThis : window);
