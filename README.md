# Two Agent Lab — Lecture 0

Cheap Worker + strong Reviewer. Python owns the loop.

```text
Task → Worker (DeepSeek) → Reviewer (GPT-5.6 Sol)
              ↑ FAIL              | PASS
              └── revise (max 2)  └── save
```

## What this version does

- Desktop chat window (`start.vbs`). No command prompt stays open.
- Worker writes. Reviewer says PASS or FAIL.
- If the task needs a file (HTML, game, script), the Worker must put complete code in a fenced block. Python fails the run if it only gets a write-up.
- Each run saves a report and JSON in `outputs/`. Code fences become real files there.
- The chat has no memory. Each send is a new task.
- Offline tests do not call any API.

## Requirements

- Python 3.10+ (3.11 or 3.12 on Windows; 3.13 can hang on `asyncio`)
- [DeepSeek API key](https://platform.deepseek.com/api_keys) for the Worker
- [OpenAI API key](https://platform.openai.com/api-keys) for the Reviewer

Defaults: `deepseek-v4-flash` and `gpt-5.6-sol`.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Put both keys in `.env`. Never commit `.env`.

## Run

Windows: double-click `start.vbs` (or `start.bat`). Type a task. Send.

Or:

```text
.venv\Scripts\python.exe app.py
```

Terminal:

```text
.venv\Scripts\python.exe main.py --task "Explain recursion with a short Python example."
```

Files land in `outputs/`. HTML and other code files are extracted there. Open them yourself.

## Test

```text
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Files

| File | Role |
| --- | --- |
| `app.py` | Desktop chat |
| `main.py` | Agents, loop, save |
| `start.vbs` / `start.bat` | Launch the chat |
| `.env.example` | Key template |
| `tests/test_main.py` | Offline loop tests |

## Limits

- Reviewer PASS is a model judgment, not a proof.
- “Needs a file” is keyword-based (`html`, `game`, `build a`, …), not a perfect classifier.
- No tools, sandbox, or shared memory between sends.
- Windows `Runner.run_sync` can freeze, so model calls use the sync OpenAI client.
