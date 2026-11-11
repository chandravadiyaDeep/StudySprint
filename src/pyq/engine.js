/* Orchestrates the versioned PYQ baseline; all findings retain source-paper examples. */
(function (root) {
  "use strict";

  const ENGINE_VERSION = "lexical-baseline-0.1";
  const GROUP_THRESHOLD = 0.62;

  function analyzeDocuments(documents) {
    const extracted = [];

    documents.forEach((document, paperIndex) => {
      root.StudySprintPYQ.splitQuestions(document.text).forEach((question) => {
        extracted.push({
          ...question,
          paperName: document.name || ("Paper " + (paperIndex + 1)),
          paperIndex,
          normalized: root.StudySprintPYQ.normalizeQuestion(question.raw)
        });
      });
    });

    if (!extracted.length) {
      throw new Error("No reliable question candidates were extracted. Try text-based PDFs or clearer TXT files.");
    }

    const groups = [];
    extracted.forEach((question) => {
      let bestGroup = null;
      let bestScore = 0;

      // Compare against group members; keep grouping logic isolated for future algorithm swaps.
      groups.forEach((group) => {
        group.members.forEach((member) => {
          const score = root.StudySprintPYQ.jaccardSimilarity(question.normalized, member.normalized);
          if (score > bestScore) {
            bestScore = score;
            bestGroup = group;
          }
        });
      });

      if (bestGroup && bestScore >= GROUP_THRESHOLD) {
        bestGroup.members.push(question);
      } else {
        groups.push({ members: [question] });
      }
    });

    return {
      engineVersion: ENGINE_VERSION,
      method: "token-jaccard",
      threshold: GROUP_THRESHOLD,
      extractedQuestionCount: extracted.length,
      groups: groups.map((group, index) => {
        const paperNames = [...new Set(group.members.map((member) => member.paperName))];
        const representative = group.members.slice().sort((a, b) => b.raw.length - a.raw.length)[0];

        return {
          id: "pattern-" + (index + 1),
          label: representative.raw.slice(0, 145),
          count: group.members.length,
          paperCount: paperNames.length,
          paperNames,
          confidence: group.members.length > 1 ? "lexical-match" : "single-observation",
          examples: group.members.slice(0, 5).map((member) => ({
            paper: member.paperName,
            question: member.raw,
            segmentationMethod: member.segmentationMethod
          }))
        };
      }).sort((a, b) => b.paperCount - a.paperCount || b.count - a.count)
    };
  }

  root.StudySprintPYQ = root.StudySprintPYQ || {};
  root.StudySprintPYQ.ENGINE_VERSION = ENGINE_VERSION;
  root.StudySprintPYQ.analyzeDocuments = analyzeDocuments;
})(typeof globalThis !== "undefined" ? globalThis : window);
