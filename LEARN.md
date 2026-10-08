# LEARN: walk through the AI governance pack

This file is for Sara. Use it to practise explaining the pack out loud before an interview.

## 1. A 10-minute walkthrough script

**Minute 0–1. The one-liner.** "This is the launch pack for my customer-service agent, P1. It has a system card, a risk register, an EU AI Act memo, a NIST AI RMF mapping, UAE data-protection notes, red-team findings and an oversight runbook. The twist is that every claim points to a real test or eval file. A small validator in CI stops me from marking a risk 'verified' before the evidence exists."

**Minute 1–3. The system card** (`governance/01_system_card.md`).

- Show the "can / cannot" table, and the design choice: the model understands messages and writes replies, while plain code decides tools, identity checks and approvals.
- Point at section 7: the exact disclosure text in Arabic, English and French.
- Point at section 8:
  - the live agent on `openai/gpt-6-luna` had **0/120** violations and 97.5% task success;
  - the same model as a plain chatbot, without the code guards, broke a rule in 120/120 conversations;
  - P3's red-team: 45/45 attacks blocked.
- Say clearly that the tone and quality scores come from an LLM judge, not from people.

**Minute 3–5. The risk register** (`governance/risk_register.csv` and `02_risk_register_summary.md`).

- Explain the rating rule: Low = 1, Medium = 2, High = 3, likelihood × impact.
- Go through the top 3 risks:
  - **R02 prompt injection (Critical, verified for known attacks).** The model cannot approve anything. The proof:
    - a test with a fake model that *obeys* the attack: the refund still waits for a supervisor;
    - 15/15 live injection conversations right;
    - 18/18 P3 injection and jailbreak attacks blocked.
  - **R01 cross-customer leak (High, verified).** Verification happens first. Our own probe found that the second-layer filter missed phone-number variants (DR-1). P1 fixed it, and the re-test caught 6 of 6.
  - **R15 weak oversight (High, Open).**
    - The on-screen role choice is gone, but there is no sign-in yet.
    - One angry-customer script was not handed over to a person (RT-4).

**Minute 5–6. The evidence index and the validator.**

- Open `evals/evidence_index.csv`.
  - Show that a "not run yet" row (E19, E29, E41) has an empty result column.
  - Show the two `failed` rows (E16, E27), and explain why they stay failed.
- Run `python -m governance_pack.validate_register`.
- Then show the honesty rule: put a number in a pending row and run it again. It fails.

**Minute 6–8. The law.**

- **EU AI Act** (`03_eu_ai_act_memo.md`):
  - it is *not* high-risk, because retail customer service is not in Annex III;
  - it *is* a transparency case: Article 50(1) has applied since 2 August 2026;
  - the Digital Omnibus moved the high-risk dates to December 2027 and August 2028;
  - marking text replies under Article 50(2) is the open question for counsel.
- **UAE** (`05_uae_data_protection_notes.md`):
  - the PDPL is in force, but its Executive Regulations are still pending;
  - sending chat text to a model provider abroad is a cross-border transfer;
  - DIFC Regulation 10 asks for a notice at first use.

**Minute 8–9. NIST and red-team** (`04_…`, `06_…`).

- NIST: the strongest function is Measure for the code guards, now backed by live runs. The weakest is human validation: no person has checked the LLM judge yet.
- Red-team: walk through one row in the format "what happened → fix → re-test".

**Minute 9–10. Runbook and next steps** (`07_…`).

- Who approves what, and the three switch-off levels. Level 1 is to remove the API key, and the app falls back to rules-only.
- The decision on 8 October 2026 (evening) is **No-go for real customers; Go for a supervised internal pilot.**
  - **Why real customers are still blocked:** there is no sign-in for approvers, personal data goes abroad unmasked, no human has checked the judge, and one handover miss is still open.
  - **Why an internal pilot is fine:** staff testers and synthetic data use no real personal data, and the live evidence is strong for the code-enforced controls.
  - In the afternoon, before any model was called, the decision was a plain No-go.

## 2. Ten interview questions with short model answers

1. **Is this chatbot "high-risk" under the EU AI Act?**
   - No. High-risk means Annex I (safety components of regulated products) or one of the eight Annex III areas, such as credit scoring or employment. Retail customer service is in neither.
   - It is a *transparency* case. Article 50(1) says that people must be told they are talking to an AI unless that is obvious, and it has applied since 2 August 2026.
   - I would re-check the classification if the bot were reused for something like scoring staff.

2. **How does P1 meet Article 50(1)?**
   - There are two fixed-text layers: a page banner, and a first reply added by code that says "I'm Lumi Skin's AI assistant, not a human" in the customer's language.
   - **The evidence:**
     - a P1 test in all three languages;
     - the live agent with 0/120 missing disclosures;
     - the plain-LLM baseline, which **forgot the disclosure in 120/120** conversations without the code. That is why the disclosure is added by code.
   - **The gaps:** reminders in complaint contexts, an accessibility check, and a native speaker's check of the Arabic and French banner.

3. **What are your top 3 risks, and what evidence shows the controls work?**
   - **Prompt injection.**
     - A test uses a fake model that obeys the attack, and the refund still waits for a supervisor.
     - Live: 15/15 injection conversations right, 0/120 violations.
     - P3: 18/18 injection and jailbreak attacks blocked by `gpt-6-luna`.
   - **Cross-customer leak.**
     - The verification tests pass, and the live run had 0/120 leaks.
     - Our probe first found the leak filter caught only 3 of 6 phone formats. After P1's fix: 6 of 6.
   - **Weak oversight.**
     - The supervisor rule is tested, and the on-screen role choice is gone.
     - But there is no sign-in, and one angry customer was not handed over, so that risk is Open.
   - **Limits:** small scripted sets, one run, and judge verdicts that no person has checked yet.

4. **What would you need from engineering before launch?**
   - **Done on 8 October:** the live eval (0/120), the P3 red-team, the leak-filter fix, disclosure tests in three languages, and outage tests.
   - **Still needed:**
     - sign-in on the Approvals tab;
     - a fix for the missed handover, tested on new scripts;
     - P3's unsafe-advice and discount attacks run through the full agent;
     - email and phone masking before model calls;
     - an on/off switch and alerts.

5. **How do you keep the documents current when the model changes?**
   - The change rule in the runbook. A new model ID means re-running the P1 eval and the P3 red-team, updating the model table and the evidence rows, and running the validator.
   - The validator will not let a risk stay "verified" if its evidence is reset to pending.

6. **Why separate "control built" from "control verified"?**
   - A control in code is not proof that it works with the real model.
   - "Verified" needs every linked evidence item to have actually run and passed, and the validator enforces that.
   - In the afternoon only R04 was verified. After the live runs, 7 of 15 are verified.
   - R08 and R09 are not verified: P3 tested them on bare models only, and I want a test through the full agent first.
   - R06 is not verified: the judge failed 2 policy answers, and a person has not checked them yet.

7. **What does the NIST AI RMF add if it is voluntary?**
   - It gives a checklist structure (Govern, Map, Measure, Manage) that US companies and auditors recognise.
   - Mapping our real work to it showed the gaps clearly: no monitoring, no approver training, no independent review.

8. **What does the UAE PDPL change for collecting customer data in a chat?**
   - You need a lawful basis. Contract performance covers order support; marketing needs consent.
   - You must keep a record of processing and secure the data.
   - People can object to significant automated decisions. Our human approvals keep those decisions human.
   - Sending chat text to a foreign model provider is a cross-border transfer. The Executive Regulations are still pending, so we build to the law's text and ask counsel.

9. **Your red-team found something. Walk me through it.**
   - **What happened (DR-1).** I called P1's leak filter directly with six versions of another customer's data, and it caught 3. It missed the phone number without spaces, in local format and with Arabic-Indic digits, because it matched exact strings.
   - **Why the risk was low:** other customers' data never reaches the model.
   - **The fix:** P1 now compares normalised forms. My unchanged probe then caught 6 of 6, and P1 added 25 test cases (23 other spellings of another customer's data, the six-variant probe check and a no-false-alarm check).
   - **A second example (RT-4).** The live run found one angry-customer script that was never handed over. We recorded it as failed and did not tune the prompt on that script.

10. **What are the limits of this pack?**
    - The live numbers come from small scripted sets, run once, and the quality and tone scores come from an LLM judge that no person has checked yet.
    - Not reviewed by a lawyer.
    - Two facts rest on secondary sources.
    - The same family of coding agent built P1 and reviewed it, so a human reviewer would make it stronger.

## 3. Three "change it live" exercises

1. **Add a risk.**
   - Add `R16` to `governance/risk_register.csv`: "Reply in the wrong language". Category `fairness`, Medium × Medium.
   - Link it to evidence E17 and set the status to `Control built - evidence pending`.
   - Run the validator. Then set the rating to `High` on purpose and watch the validator reject it.
   - Note: the register currently allows 10–15 risks, so you must also raise that limit in `validate_register.py` (and in its test). Ask yourself whether that limit should exist at all.

2. **Try to cheat, and get caught.**
   - In `evals/evidence_index.csv`, put "0.8" in the `result` column of E29, which is still `not run yet`. Run `pytest -q`; it fails.
   - Then change R07's status to `Control verified`. It fails again, because E19 and E29 have not passed.
   - Undo both changes. This is the "never invent results" rule as code.

3. **Add a governance rule to the validator.**
   - In `check_risk_row()`, add: "a `Critical` risk may not have the status `Accepted`".
   - Write a test in `tests/test_validate_register.py` that builds a register with such a row and expects the new message.
   - Run `pytest -q` and `ruff check .`.
