/* Explainable lexical similarity baseline. Thresholds require benchmark calibration. */
(function (root) {
  "use strict";

  function jaccardSimilarity(left, right) {
    const a = root.StudySprintPYQ.tokenSet(left);
    const b = root.StudySprintPYQ.tokenSet(right);
    if (!a.size || !b.size) return 0;

    let intersection = 0;
    a.forEach((token) => {
      if (b.has(token)) intersection += 1;
    });

    return intersection / (a.size + b.size - intersection);
  }

  root.StudySprintPYQ = root.StudySprintPYQ || {};
  root.StudySprintPYQ.jaccardSimilarity = jaccardSimilarity;
})(typeof globalThis !== "undefined" ? globalThis : window);
