// Node's built-in test runner verifies deterministic behavior of the browser engine modules.
const test = require("node:test");
const assert = require("node:assert/strict");

require("../src/pyq/question-segmentation.js");
require("../src/pyq/normalization.js");
require("../src/pyq/similarity.js");
require("../src/pyq/engine.js");

test("segments numbered questions and preserves original wording", () => {
  const questions = globalThis.StudySprintPYQ.splitQuestions(
    "Q1 Explain linked list insertion.\nQ2 Describe stack operations."
  );
  assert.equal(questions.length, 2);
  assert.match(questions[0].raw, /linked list insertion/i);
});

test("normalizes question text without mutating source strings", () => {
  const raw = "Q2: Explain Stack Operations!";
  assert.equal(globalThis.StudySprintPYQ.normalizeQuestion(raw), "explain stack operations");
  assert.equal(raw, "Q2: Explain Stack Operations!");
});

test("groups similar questions and keeps their paper evidence", () => {
  const result = globalThis.StudySprintPYQ.analyzeDocuments([
    { name: "Paper 2022", text: "Q1 Explain operations of a singly linked list with example." },
    { name: "Paper 2023", text: "Q1 Explain operations of a singly linked list with an example." }
  ]);
  assert.equal(result.engineVersion, "lexical-baseline-0.1");
  assert.equal(result.extractedQuestionCount, 2);
  assert.equal(result.groups[0].paperCount, 2);
  assert.deepEqual(result.groups[0].paperNames, ["Paper 2022", "Paper 2023"]);
});

test("rejects documents with no question candidates", () => {
  assert.throws(
    () => globalThis.StudySprintPYQ.analyzeDocuments([{ name: "empty", text: "" }]),
    /No reliable question candidates/
  );
});
