# StudySprint

**Your syllabus. Your exam strategy. Your daily execution.**

StudySprint is an early-stage, browser-only academic planning experiment. It helps students turn syllabus text into editable learning goals and inspect historical topic patterns in previous-year papers.

## Validation build

- Glassmorphism-inspired responsive interface
- Syllabus text extraction from selectable-text PDF, TXT and Markdown files
- Editable unit/topic learning checklist
- PYQ text extraction and syllabus-keyword matching across multiple papers
- Transparent historical frequency indicators
- Focus timer and exam countdown
- Local browser storage and JSON data export

## Intelligence engine specifications

The two core engines are being designed independently. Their algorithm choices, evidence requirements, evaluation plans, API contracts, and release criteria are documented here:

- [Syllabus Intelligence Engine](docs/syllabus-intelligence.md)
- [PYQ Intelligence Engine](docs/pyq-intelligence.md)

These are engineering specifications, not claims that the engines are already implemented. The current website remains a browser-only validation prototype; the backend and measured algorithms are future implementation work. The system must abstain when evidence is weak and must never present historical frequency as a guaranteed exam prediction.

## Run locally

Open `index.html` in a modern browser. PDF reading uses PDF.js from a public CDN, so an internet connection is needed for PDF files. TXT and Markdown parsing works without that library.

## GitHub Pages

The site is a static website. In repository Settings → Pages, select **Deploy from a branch**, choose `main` and `/(root)`. The expected project URL is:

https://chandravadiyaDeep.github.io/StudySprint/

Allow a few minutes after the first deployment.

## Important limitations

- This is a validation prototype, not a production academic AI system.
- Syllabus parsing uses simple heading and text heuristics. Review and edit the generated structure.
- PYQ matching uses keyword matching against the syllabus topics. It is not semantic AI and may miss paraphrases or create false matches.
- Scanned/image-only PDFs are not OCR-processed in this version.
- No private API key is required or included.
- Data is stored in the current browser only. Clearing browser data can erase it. There is no account, cloud sync or backup.
- Historical PYQ frequency is not a prediction of future examination questions.

## Validation questions

1. Could you understand the syllabus breakdown without help?
2. Were the extracted topics accurate?
3. Did the PYQ report help you decide what to study next?
4. What was confusing, missing or incorrect?
5. Would you use this before your next exam?

StudySprint is being validated with real students before expanding its feature set.
