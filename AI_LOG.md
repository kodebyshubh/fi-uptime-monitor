# AI Collaboration Log

This is a running log, updated as I build, not written after the fact. See also [`prompts.md`](prompts.md) for the cleaned-up, phase-wise version of this same build — this file is the raw, unedited record; `prompts.md` is what I'd hand someone to redo it from scratch.

## AI Tech Stack

- **Claude Code** (CLI agent), model: **Claude Sonnet 5**, running directly in my editor/terminal with file read/write/edit and bash/shell execution tools.
- Used it as the primary driver for both backend (FastAPI/Python) and frontend (React/Vite) code, since my own background is backend/infra-heavy and the frontend layer is the explicit "stretch" part of this assignment.

## The Prompts That Shipped It

Raw prompts, in order, first person:

1. "read all the files in ztask, and gather what should be done to achieve this, i want to excel in this, while learning what i am building and being answerable to any question that can be asked against this assignment"
   - This kicked off Claude reading `ztask/ai assignment.md`, `ztask/email.md`, `ztask/praveen.md` and summarizing the actual grading criteria before writing any code.
2. Answered a stack-choice prompt from Claude (multiple-choice): chose **Python + FastAPI + SQLite** for backend, **React (Vite)** for frontend, and **step-by-step collaborative build** (small chunks, explained as we go) over "AI builds it all, I review after."
3. "yes and manyall aproove edits also maitnail a claude.md file" — approved the build plan, asked that edits go through manual approval (no auto-accept) and that a `CLAUDE.md` be kept up to date describing the project as it's built.
4. "where were we" — resumed after an interruption; Claude re-summarized progress instead of re-doing work.
5. Answered a verify-step prompt: chose to install deps in a venv and curl-test the backend locally before touching Docker, instead of jumping straight to containerizing.
6. "yes, but also keep track of the prompts that i am using to build this, refer ztask/ai assignment.md for this and prepare a md rn and store all the prompts from my first person POV in it till now, and record all the other things that are mentioned in ai assignment.md in the way it was mentioned while building" — this prompt, which started this file.

7. "yes i am able to see it" — confirmed the frontend rendered correctly against the live backend (up/down badges, latency, timestamps all showing real data) before moving on to Docker.
8. "wait tell me how to check everything till now, update the claude md till now same for ai_log md, and tell me detailed steps to docker step i will do it manually" — paused the AI-driven build here; asked for a status recap and to write the Dockerfiles/compose myself by hand rather than have Claude generate them, to actually learn that layer.

9. "explain me this error and record this in a suitable file also, after reading ztask/ai assignment.md" — hit a port-8000-already-in-use error trying to run the backend myself; asked Claude to explain it and log it.

10. "help me create the file and pasting the code inside it one by one" — reversed the earlier call to write Docker files by hand; had Claude create `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` directly instead, one at a time.
11. Ran `docker compose up --build` myself, pasted the full build log back and asked "what should i do now" — confirmed both containers built and started cleanly.
12. Hit the recurring `curl.exe` JSON-quoting failure again inside the fresh Docker container test; switched to `Invoke-RestMethod` per Claude's suggestion and both test URLs registered successfully.
13. Registered a third, arbitrary URL (`google.com`) myself beyond the two required test cases and asked "is this correct?" — confirmed the app isn't hardcoded to just the two demo URLs, it correctly tracks any registered URL.
14. "before writing readme, what i want you to do is: 1) scan the complete project and draft a phase-wise structured detailed prompt to build this project as if starting from scratch, first-person POV, in `prompts.md` — incorporating everything from `ztask/task.md`. 2) read `ztask/task.md`'s submission format points 2 and 3, and write `AI_LOG.md` and `README.md` to match those requirements exactly." — this prompt, which produced `prompts.md` and finalized this file plus the README.

## Status

Backend, frontend, and Docker are all built and verified end-to-end (see repro steps in `README.md`). This log and `prompts.md` are the final versions submitted alongside the code.

## The Course Corrections

- **Vite's default template styling fought the actual UI.** `npm create vite@latest` scaffolds a marketing-landing-page layout (`#root` fixed at `1126px` width, flex-centered hero section, big decorative headings) baked into `index.css`/`App.css`. That's fine for a demo template but actively wrong for a data table dashboard — it would have center-aligned and width-capped the monitor table in a way that looks broken. Caught it by reading the generated CSS before wiring `App.jsx` into it, and replaced both files outright (plain reset in `index.css`, a small table/badge stylesheet in `App.css`) rather than patching over template rules one at a time.
- **Port conflict from a leftover background process Claude started.** While verifying the backend earlier, Claude launched `uvicorn` in the background (via its own tooling) to curl-test the API, and never tore it down after moving on to the frontend step. When I later tried to run `uvicorn main:app --port 8000` myself in my own terminal to do the Docker step, it failed: `ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000): [winerror 10048] only one usage of each socket address (protocol/network address/port) is normally permitted`. Not a code bug — the app itself is fine — but a process-hygiene miss on Claude's part: it should have killed its background verification server once it was done with it. Fixed by finding the stale process (`netstat -ano | grep :8000`, PID 3740) and killing it, freeing the port.
- **`curl.exe` JSON body quoting on Windows kept failing, three different ways.** Testing `POST /monitors` from PowerShell hit the same wall repeatedly: first `\"`-escaped quotes got mangled by PowerShell's own tokenizer; then single-quoted JSON bodies (`-d '{"url":"..."}'`) *still* failed even run one-at-a-time, with the backend reporting `"input":{}` — meaning curl.exe's own C-runtime argv parser was stripping the embedded `"` characters before the JSON ever left the machine, independent of the shell. Recognized this wasn't a one-off typo (it recurred across multiple quoting styles) and stopped trying to out-clever curl's Windows argument parsing. Switched the whole test workflow to PowerShell-native `Invoke-RestMethod -Body (@{url="..."} | ConvertTo-Json)`, which builds the JSON from a hashtable instead of a hand-quoted string — sidesteps the problem entirely. Both test URLs registered successfully on the first try after the switch. Also flagged this for the README's test section, since a grader on Windows will hit the identical wall.
- More entries to be added as they occur (not backfilled).
