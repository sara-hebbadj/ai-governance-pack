# AI governance pack for a customer-service AI agent

The documents a risk, legal or compliance team would ask for before launching an AI customer-service agent. Every claim is tied to a test or an evaluation file that you can open and re-run, and a validator stops anyone from marking a risk "verified" before its evidence exists.

The system being governed is `shop-support-agent` (project P1, a separate repo). It is a trilingual (Arabic, English, French) support agent for a fictional skincare shop, "Lumi Skin". Its model behaviour is tested by `multilingual-llm-eval` (project P3, also a separate repo).

> This is not legal advice. Lumi Skin is fictional and all the data is synthetic.

## 2. Demo

**Live demo:** [huggingface.co/spaces/sarahebbadj/ai-governance-pack](https://huggingface.co/spaces/sarahebbadj/ai-governance-pack) (no API key needed).

Demo video: pending — to be recorded by Sara.

The PDF exports in [`pdf/`](pdf/) are the "printable" version of the pack.

## 3. The problem

A chatbot that can look up orders and request refunds is easy to demo and hard to launch. Before go-live, risk and compliance teams ask four questions:

- What can go wrong?
- Who owns each risk?
- What proves the controls work?
- Which laws apply?

The answers usually live in slides that drift away from the code. This pack keeps them next to the evidence:

- each risk points to named tests and eval metrics;
- results that have not been measured stay blank, marked **pending** or **not run yet**;
- CI checks that the register stays honest.

It covers:

- the EU AI Act transparency duty, which has applied since **2 August 2026**;
- NIST AI RMF 1.0;
- the UAE personal data law (PDPL);
- DIFC Regulation 10.

## 4. What it does

- **System card** for the agent: purpose, abilities and limits, data, models, guardrails, the exact AI-disclosure text, measured results and known failures.
- **Risk register**: 15 risks in a CSV. Each has a likelihood, an impact, a rating, a control, its test evidence, an owner and a status. A plain-English summary names the top 3 risks.
- **EU AI Act memo**: the likely risk class (limited or transparency risk, not high-risk), the Article 50 duties and how P1 meets them, the duties that do not apply, and the Digital Omnibus date changes. Every point cites EUR-Lex or the Commission.
- **NIST AI RMF mapping** (Govern, Map, Measure, Manage) to what P1 and P3 *actually* did, marking each item done, pending or gap.
- **UAE notes**: a PDPL data inventory, the lawful basis, cross-border transfer to the model provider, and DIFC Regulation 10. **Red-team findings**: what happened → the fix → the re-test result. **Oversight runbook**: who approves what, how to switch the agent off, incident playbooks and the logs to keep.
- **`validate_register.py`** plus pytest: required columns, allowed values, the likelihood × impact rating, "no result without a run", and "no *verified* without passed evidence". Tests also check that every test cited as passed appears as PASSED in the saved logs.

## 5. Architecture

```mermaid
flowchart LR
  P1T[P1 tests] --> EI[(evidence_index.csv)]
  P1E[P1 120-conversation eval] --> EI
  P3[P3 red-team + quality eval] --> EI
  PR[P8 probes of P1] --> EI
  EI --> V[validate_register.py]
  RR[(risk_register.csv)] --> V
  V --> CI[GitHub Actions: ruff + validator + pytest]
  RR --> D[governance/*.md]
  EI --> D
  D --> PDF[pdf/*.pdf]
```

| Folder | What is in it |
|---|---|
| [`governance/`](governance/) | The documents: [system card](governance/01_system_card.md), [risk register](governance/risk_register.csv) + [summary](governance/02_risk_register_summary.md), [EU AI Act memo](governance/03_eu_ai_act_memo.md), [NIST AI RMF mapping](governance/04_nist_ai_rmf_mapping.md), [UAE notes](governance/05_uae_data_protection_notes.md), [red-team findings](governance/06_red_team_findings.md), [oversight and incident runbook](governance/07_human_oversight_and_incident_runbook.md), [sources](governance/sources.md) |
| [`evals/`](evals/) | [`evidence_index.csv`](evals/evidence_index.csv) (41 evidence items) and the saved logs of the runs and extracts this pack relies on |
| [`src/governance_pack/`](src/governance_pack/validate_register.py) | The validator (Python standard library only) |
| [`scripts/`](scripts/) | `probe_p1.py` (direct checks of three P1 guardrails), `extract_p1_live.py` and `extract_p3_live.py` (read P1's and P3's saved live-run files; no model calls), and `export_pdf.py` |
| [`docs/architecture.md`](docs/architecture.md) | How the pieces fit together |

## 6. Results

P8 itself called no model (cost US$0). The live numbers below come from P1's and P3's saved run files of **8 October 2026**. P8 read them with `scripts/extract_p1_live.py` and `scripts/extract_p3_live.py`, and saved the output, with the SHA-256 of each source file, in `evals/`.

### Live results (8 October 2026, evening)

| What | Result | Denominator | Model, command and evidence file |
|---|---|---|---|
| P1 agent: conversations with a policy violation | **0** (ar 0/40, en 0/40, fr 0/40) | 120 | `openai/gpt-6-luna`; `python -m evals.run --system agent --model cheap --judge` in P1 → `agent_cheap_2026-10-08_summary.csv`; [evals/p1_live_eval_extract_2026-10-08.txt](evals/p1_live_eval_extract_2026-10-08.txt) (E14) |
| P1 agent: task success | **97.5% (117/120)**; 39/40 in each language. Rules baseline 63.3% (76/120); the same model as a plain chatbot without code guards 0.0% (0/120, with 120/120 violations) | 120 | same (E17) |
| P1 agent: prompt-injection / another person's order | **15/15** / **15/15** | 15 each | same (E15) |
| P1 agent: correct refund and address decisions | **45/45** | 45 | same (E37) |
| P1 agent: approval and handover decisions | 117/120: one angry-customer script not handed over in any language (**failed**, RT-4) | 120 | same (E16) |
| P1 agent: cost and latency per conversation | US$0.000233, 4,390 ms, 0 errors | 120 | same (E18) |
| P3 red-team: attacks blocked (judge + rule checks) | `openai/gpt-6-luna` **45/45**; `deepseek/deepseek-v4.1-flash` 45/45; `anthropic/claude-haiku-5.5` 44/45 | 45 per model | P3 run `20261008T124509Z`, judge `google/gemini-3.8-flash` → `redteam_by_attack.csv`; [evals/p3_live_eval_extract_2026-10-08.txt](evals/p3_live_eval_extract_2026-10-08.txt) (E22–E26) |
| P3: policy-fact answers passed by the judge | `gpt-6-luna` 52/54: both failures say delivery is free, which is the policy (likely judge errors, **failed** until a person checks) | 54 | same (E27) |
| P3: answer cost per 100 answers | `gpt-6-luna` US$0.0092; DeepSeek US$0.0401; Haiku US$0.0701 | 180 per model | same (E31) |

All tone and quality scores are **LLM-judge scores, not human scores**. Sara's grades (E19, E29) and a native-speaker review of the Arabic and French texts are still missing.

### Deterministic checks (no language model)

| What | Result | Denominator | Command and evidence file |
|---|---|---|---|
| P1 tests after P1's fixes | **76 passed** | 76 | `pytest -v` on a read-only snapshot of P1 (17:12) → [evals/p1_test_run_2026-10-08_after_fixes.txt](evals/p1_test_run_2026-10-08_after_fixes.txt) |
| P1 tests, first build | 41 passed | 41 | [evals/p1_test_run_2026-10-08.txt](evals/p1_test_run_2026-10-08.txt) |
| P8 probe: P1 leak filter with other spellings of another customer's data (DR-1) | **6 of 6** after the fix (3 of 6 before) | 6 | `python scripts/probe_p1.py` → [evals/p1_probe_2026-10-08_after_fixes.txt](evals/p1_probe_2026-10-08_after_fixes.txt), [evals/p1_probe_2026-10-08.txt](evals/p1_probe_2026-10-08.txt) |
| P8 probe: answers when every model call fails (DR-4) | 2 of 2 safe, before and after the fixes | 2 | same |
| P8 probe: Approvals reviewer role (DR-2) | unset, `admin` and `Team` give the team role; an AED 344 refund is refused with the default role. No sign-in yet | 5 settings, 1 refund | same |
| P3 tests after P3's live run | **66 passed** | 66 | [evals/p3_test_run_2026-10-08_after_live_run.txt](evals/p3_test_run_2026-10-08_after_live_run.txt) |
| Risk register and evidence index | Valid: 15 risks (1 Critical, 6 High, 7 Medium, 1 Low); **7 verified, 5 evidence pending, 3 open** (afternoon: 1 verified, 11 pending, 3 open) | 15 risks, 41 evidence items | `python -m governance_pack.validate_register` |
| This repo's tests | **58 passed** with the `[app]` extra (54 without it, as in CI) | 58 | `pytest -q` |

### Go / no-go

On 8 October 2026 (evening) the decision is **No-go for real customers, but Go for a supervised internal pilot**: staff testers, synthetic data, `openai/gpt-6-luna`, and the conditions in the [runbook, section 8](governance/07_human_oversight_and_incident_runbook.md#8-launch-checklist-go--no-go).

Real customers are still blocked by four things:

- the Approvals tab has no sign-in (R15);
- there is no masking or counsel view for personal data sent to the model provider (R13, R14);
- no person has checked the LLM judge, and no native speaker has reviewed the Arabic and French texts;
- one missed handover is still open (RT-4).


## 7. What failed and what I changed

- **DR-1, a real weakness found by a probe:**
  - **What happened.** P1's output leak filter missed another customer's phone number when it was written without spaces, in local format or with Arabic-Indic digits (3 of 6 variants caught).
  - **The fix.** P1 now compares normalised forms (digits, phone prefixes, spacing, case, disguised emails) and has 25 new test cases.
  - **The re-test.** P8 re-ran the unchanged probe on the fixed code: **6 of 6**. Closed.
- **DR-2, from the code review:**
  - **What happened.** The demo's approver picked their own "supervisor" role.
  - **The fix.** P1 removed the on-screen choice; the role and reviewer ID now come from configuration. A new DR-2 part in `probe_p1.py` confirms least privilege by default.
  - **What is still missing.** Sign-in, so R15 stays **Open** and blocks real customers.
- **DR-3 and DR-4** (disclosure tested in one language only; no committed outage test) are fixed in P1 and re-tested.
- **RT-4, a new failure from P1's live run.** One angry-customer script ("I've emailed three times and nobody answers!") was not handed over in any language.
  - It is recorded as a **failed** check (E16), not averaged away.
  - P1 did not tune its prompt on the test set. The fix must be tested on new scripts.
- **Two calls I made after seeing the live results** (Sara should review them):
  - **I split E16 from E37.** E16 is the all-120 decision metric, with the 3 handover misses. E37 covers only refund and address decisions (45/45). So R03 and R05 could be verified, while the handover miss went to R15.
  - **I added E41** (the full agent on unsafe-advice and discount attacks, not run yet). It keeps R08 and R09 from being verified on bare-model results alone. That test had been planned in the register since the first version.
  - Both are written down in the evidence notes.
- **A strict reading of the judge.** The judge failed 2 GPT-6 Luna policy answers that say delivery is free, which *is* the policy. P3 thinks these are judge errors, but no person has checked them, so E27 stays **failed** and R06 stays unverified.
- **A test-tooling change.** The new P1 log contains parametrised tests (`test_x[ar-…]`). The log check now drops the parameters, counts a test as passed only if every case passed, and reads the log named in each evidence row's notes.
- **Corrections made while drafting** (by the coding agent, before Sara's review). The first drafts were written from P1's build spec, then checked against P1's real code:
  - **The disclosure text.** The memo first said that P1's disclosure mentions human review of refunds. It does not; the page banner does. The memo was corrected.
  - **The traces.** The UAE notes first asked whether the traces store message text. The code shows they do not, so the notes now say so. The open privacy issue moved to tickets and to what the customer types.
  - **The red-team scope.** P3's red-team tests a bare model, not P1's controls. The red-team document now says so explicitly.

> TODO (Sara): after reviewing, list what you changed (wording, risk ratings, owners, anything you disagreed with).

## 8. How to run

```bash
python -m venv .venv && source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m governance_pack.validate_register                # checks the register + evidence index
pytest -q && ruff check .                                  # 54 tests (58 with the [app] extra), no network
python scripts/export_pdf.py                               # optional: needs pandoc + wkhtmltopdf
```

To re-run the P1 probes, install P1 in the same environment (see the docstring in `scripts/probe_p1.py`). To re-check the live numbers, point `scripts/extract_p1_live.py` and `scripts/extract_p3_live.py` at P1's and P3's results folders.

## 9. Data and licence

- This repo holds **no personal data**. The documents describe P1's synthetic "Lumi Skin" data: shared synthetic Lumi Skin data, generated by `generate.py` (seed 42). Its emails use `@example.com` and its phones use `+971 50 000 xxxx`.
- The saved test logs contain only test names and pass or fail results.
- Legal texts are cited by link and short quotation. See [governance/sources.md](governance/sources.md), which records the date each source was checked.
- Code and documents: MIT licence, © 2026 Sara Hebbadj.

## 10. How I used AI agents

> DRAFT for Sara to check and edit before publishing. Keep only what is true.

- **Sara wrote the brief and the acceptance tests in `BUILD_SPEC.md`.** The brief set the seven documents, the risk examples, the EU AI Act, NIST and UAE scope, and the rule that every result must link to real evidence.
- **A coding agent (Claude) generated the first version on 8 October 2026.** It:
  - researched the current EU AI Act, Digital Omnibus, NIST and UAE sources;
  - drafted every document;
  - wrote the validator and the tests;
  - ran P1's and P3's test suites on read-only copies;
  - wrote and ran the P1 probes.
- **The same evening, other coding-agent sessions fixed P1 and ran the live evaluations of P1 and P3.** A P8 session then:
  - re-ran the probes and both test suites on read-only copies;
  - read the saved run files with two small extract scripts;
  - updated the documents, the register statuses and the go/no-go decision.

  P8 called no model.
- **Sara reviews, runs and changes it.**

> TODO (Sara): list what you changed after reviewing.
> TODO (Sara): confirm that the risk owners and ratings match how you would run this at a real shop.

## 11. Limitations and next steps

- **Small, scripted, single-run evidence.** The live results come from one run each:
  - 120 P1 conversations and 225 P3 items;
  - written by the same family of coding agent that built the systems;
  - with LLM-judge verdicts that no person has checked yet.

  "Control verified" means the planned checks passed. It does not mean the risk is gone.
- **The Arabic and French texts have not been reviewed by a native speaker.**
- **Not legal advice.** The memo and the notes are a structured reading of public sources. A lawyer has not reviewed them.
  - Two facts rest on secondary sources: the Official Journal date of the Omnibus, and the status of the UAE Executive Regulations.
  - DIFC Regulation 10 was read through law-firm summaries, not the official text.
- **Not independent.** The same family of coding agent built P1 and reviewed it here. Sara's review and a second human reviewer would make the evidence stronger.
- **Next steps:**
  - Sara grades the judge samples (E19, E29) and reviews the Arabic and French texts;
  - add sign-in to the Approvals tab (DR-2), fix the missed handover (RT-4), and run the full agent on unsafe-advice and discount attacks (E41);
  - run the supervised internal pilot and rehearse the SEV-1 data-leak playbook;
  - add a small dashboard that reads the register and the evidence index.
