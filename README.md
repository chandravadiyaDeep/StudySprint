# StudySprint

**PYQ Intelligence first. Evidence before predictions.**

StudySprint is an early-stage product focused on analyzing previous-year question papers. The active scope is intentionally narrow: upload authentic papers, extract question candidates, find repeated or similar questions, and inspect the source evidence behind every result.

## Active scope
- Responsive glassmorphism-inspired interface.
- Multiple PDF, TXT and Markdown uploads.
- Browser-side text extraction using PDF.js for text-based PDFs.
- Initial question segmentation and lexical similarity grouping.
- Pattern report showing occurrence counts, paper names and original question examples.
- Focus timer, exam countdown and local profile settings.
- Local browser storage; no account or cloud sync in this prototype.

## Research specifications
- [PYQ Intelligence Engine — active specification](docs/pyq-intelligence.md)
- [Syllabus Intelligence Engine — deferred specification](docs/syllabus-intelligence.md)

Syllabus Intelligence has been removed from the active UI and workflow. Its document is retained only as a future research track. Do not implement it until the PYQ engine meets its quality gates.

## Important truth about the current build
The current PYQ implementation is a **browser-only baseline**, not a production reasoning engine and not yet connected to an AI API. It uses question-number/paragraph segmentation and lexical token similarity. It can miss paraphrases, split questions incorrectly or group unrelated questions. Synthetic demo papers are labelled synthetic and must never be treated as real exam evidence.

The product must never claim a future question is guaranteed, present historical frequency as a probability, invent topic names/marks/source references, or hide extraction failures.

## Planned architecture
GitHub Pages serves only the static frontend. A future Python/FastAPI backend will handle secure uploads, page-aware extraction, background analysis jobs, semantic retrieval/reranking, source evidence and versioned algorithms. Any private model/API key must remain in backend environment variables. Never put a private API key in index.html, JavaScript or a public GitHub repository.

Evaluate the engine on human-labelled papers before selecting semantic models or making quality claims. See the PYQ specification for the API contract, metrics and release gates.

## Run locally
Open index.html in a modern browser. PDF extraction uses PDF.js from a CDN, so an internet connection is required for PDF files. TXT and Markdown extraction works directly in the browser.

## GitHub Pages
The workflow in .github/workflows/deploy-pages.yml deploys the static site on pushes to main. Expected project URL:

https://chandravadiyadeep.github.io/StudySprint/

Check the repository Actions tab for the deployment result.

## Privacy
Files and analysis results stay in the current browser in this prototype. There is no cloud upload or API call. Clearing browser storage can remove saved progress. A future backend must include explicit consent, retention and deletion controls before processing user papers.

## Validation questions
1. Did question boundaries match the original paper?
2. Were repeated/similar questions grouped correctly?
3. Did every pattern show the correct source paper and question text?
4. Which false matches or missed repeats did you find?
5. Would the report genuinely change how you prepare?
