# EU AI Act memo: the Lumi Skin customer-service assistant

| | |
|---|---|
| **To** | Lumi Skin leadership, compliance lead, engineering lead |
| **From** | Sara Hebbadj (AI governance analyst). Drafted with help from a coding agent; Sara reviews it. |
| **Date** | 8 October 2026. The facts were checked against the sources listed in [sources.md](sources.md) on this date. |
| **System** | The customer-service AI assistant of the fictional skincare shop Lumi Skin ("Lumi" for short in this memo). The repo is `shop-support-agent` (project P1). |
| **Status** | Draft for review by qualified EU counsel |

> **This is not legal advice.** It is a structured reading of public sources, written for a portfolio project about a fictional company. A qualified lawyer must review it before anyone relies on it.

## 1. The question and the short answer

**Scenario.** Lumi Skin is a fictional online shop based in Dubai. Today it delivers only to the UAE and the GCC. This memo assumes that it starts selling to customers in the EU (France and Belgium are the obvious first markets, because the assistant already speaks French), or that people in the EU use the chat. The question is what the EU AI Act asks of Lumi Skin for this assistant.

**Short answer.**

1. **Lumi is most likely a "limited-risk" (transparency) AI system.** It is not a prohibited practice, and it is not high-risk. None of the eight Annex III areas covers retail customer service, and the assistant is not a safety component of a regulated product.
2. **The main duty is Article 50(1): people must be told that they are talking to an AI.** This duty has applied since **2 August 2026**. Lumi Skin builds the assistant and runs it under its own name, so it is most likely the **provider**, and it is also the **deployer**.
3. **A second duty may apply: Article 50(2), machine-readable marking of AI-generated text.** It may cover the chat replies. This is the main open question for counsel (section 5.2). Systems that were on the market before 2 August 2026 have until **2 December 2026** to comply. The Digital Omnibus set this date.
4. **The AI-literacy duty (Article 4) also applies**, to the staff who run and supervise the assistant.
5. **P1 already shows an AI disclosure.** There is a page banner, and the first reply of every chat says, in the customer's language, that it is an AI assistant and not a human. Section 5.1 gives the details and the test evidence.

## 2. The facts this memo relies on

These facts come from the [system card](01_system_card.md).

- **What it does.** Lumi answers product, order and policy questions in Arabic, English and French. It tracks orders through a courier API and reads a CRM. It can open tickets and add notes. It can only *request* a refund or an address change; a person approves or denies each request in an approvals queue.
- **Who uses it.** Members of the public who shop online (consumers), and Lumi Skin's customer-care staff, who review the approvals.
- **What it does not do.** It does not decide on credit, insurance, employment or access to essential services. It does not analyse faces or voices. It does not publish news or other public-interest content. It does not generate images, audio or video.
- **Models.** Lumi uses general-purpose large language models from third parties, reached through OpenRouter. The model IDs are set in configuration (`MODEL_MAIN`, `MODEL_CHEAP`). Lumi Skin does not train any model.

## 3. Does the AI Act apply to a Dubai company?

**Probably yes, for EU customers.** Article 2(1)(c) covers "providers and deployers of AI systems that have their place of establishment or are located in a third country" where "the output produced by the AI system is used in the Union" [EU-2, Art. 2]. A chat reply read by a customer in France is output used in the Union.

**Roles.** A **provider** "develops an AI system ... or has an AI system ... developed and places it on the market or puts it into service under its own name or trademark" (Art. 3(3)). A **deployer** uses an AI system "under its authority" (Art. 3(4)) [EU-2, Art. 3]. Lumi Skin builds the assistant (with a contractor or coding agent) and offers it under the Lumi Skin brand, so it is most likely both. Because Lumi plugs in another company's model, Lumi Skin is also a "downstream provider" (Art. 3(68)).

## 4. Which risk class, and why

| Tier | Does Lumi fall in it? | Reasoning |
|---|---|---|
| **Prohibited practices (Art. 5)** | No | Lumi does not use subliminal or manipulative techniques, and it does not exploit vulnerabilities such as age or disability (Art. 5(1)(a) and (b)). None of the other listed practices apply either: social scoring, biometric categorisation, emotion recognition at work or school, or the new bans on sexual deepfakes and child sexual abuse material added by the Omnibus [EU-2, Art. 5]. **Design rule to keep it this way:** no pressure-selling scripts, no false urgency, and no targeting of people who say they are minors or vulnerable. |
| **High-risk (Art. 6 with Annex I or Annex III)** | No | **Annex I:** Lumi is not a safety component of a regulated product, such as a toy, a machine or a medical device. **Annex III:** its eight areas are biometrics; critical infrastructure; education; employment; access to essential private and public services (including credit scoring and life or health insurance pricing); law enforcement; migration; and justice and democratic processes. Retail customer service is not on the list [EU-2, Annex III]. The cash-on-delivery limit (AED 1,000) and the refund rules are fixed business rules. The assistant does not assess anyone's creditworthiness. |
| **Transparency (Art. 50)** | **Yes** | Lumi is "intended to interact directly with natural persons" (Art. 50(1)). It also generates text, which may bring it under Art. 50(2) (see section 5). |
| **General-purpose AI model duties (Chapter V)** | No, for Lumi Skin | These duties fall on the companies that place the underlying models on the market. Lumi Skin uses those models; it does not train them or place them on the market. |
| **Minimal risk** | Not applicable | Lumi is not minimal-risk, because Article 50 applies to it. |

**What would change the answer.** Lumi could become high-risk if it were reused for:

- scoring or monitoring customer-care staff (Annex III, point 4, employment);
- deciding who may buy on credit (Annex III, point 5(b));
- any other Annex III purpose.

If that happens, the timing is now different. The Digital Omnibus moved the start date for Annex III systems from 2 August 2026 to **2 December 2027** [EU-2, Art. 113; EU-4]. Repeat this classification **every time the assistant gets a new tool or a new purpose** (see the change rule in the [runbook](07_human_oversight_and_incident_runbook.md)).

## 5. Article 50 duties in detail

### 5.1 Article 50(1): tell people they are talking to an AI

**The law.** Providers must design the system "in such a way that the natural persons concerned are informed that they are interacting with an AI system, unless this is obvious from the point of view of a natural person who is reasonably well-informed, observant and circumspect, taking into account the circumstances and the context of use" [EU-2, Art. 50(1)]. The information must be given "in a clear and distinguishable manner at the latest at the time of the first interaction or exposure" and must "conform to the applicable accessibility requirements" (Art. 50(5)). The Digital Omnibus did not change either paragraph. The consolidated text of 27 July 2026 marks neither one as amended [EU-2].

**The Commission's guidance (20 July 2026).**

- The duty applies when four conditions are all met: the system is an AI system, it supports a two-way exchange, the AI itself communicates, and the other party is a natural person [EU-6].
- The "obvious" exception must be read narrowly [EU-6]. Law-firm summaries of the final guidelines give AI chatbots on online helpdesks as an example where the AI is *not* obvious. Their advice is "If in doubt, disclose" [EU-8].
- A generic label such as "assistant", a line in the terms of service, or metadata alone is not enough. An AI agent must say that it is an AI **and on whose behalf it acts** [EU-9].
- In complaint contexts, periodic reminders are "likely to be required" on top of the first notice [EU-8].

**How P1 does it.** P1 uses two layers of fixed text. Neither is written by the model, so neither can be "forgotten" by it.

1. **A page banner** (`app/app.py`), in English, Arabic and French: "You are chatting with an AI assistant. Refunds and address changes wait for a human…"
2. **A first-reply disclosure** added by code (`guards.disclosure()`), in the customer's language. The English version reads: "Hi! I'm Lumi Skin's AI assistant, not a human. You can ask for a person at any time." The Arabic and French versions say the same.

**Evidence** (IDs from the [evidence index](../evals/evidence_index.csv)):

- the P1 test `test_first_reply_discloses_ai_assistant` passed on 2026-10-08 for Arabic, English and French, and a test checks the three-language banner [E08];
- the rules-only baseline had **0 of 120** conversations without the disclosure (40 per language) [E13];
- the **live agent** (`openai/gpt-6-luna`, 8 October 2026) had **0 of 120** conversations with any violation, including `missing_ai_disclosure` [E14]. The same model as a plain chatbot, without the code that adds the disclosure, left it out in **120 of 120** (`shop-support-agent/evals/results/plain_cheap_2026-10-08_summary.csv`). Disclosure by code, not by prompt, is what makes it reliable;
- a P8 probe found that Arabic and English agent replies start with the disclosure even when the model is down [E36].

The exact texts are in the [system card](01_system_card.md#7-ai-disclosure-what-the-customer-sees).

**Gaps to close before an EU launch.**

- **Banner and tests in three languages: done** on 8 October 2026 (finding DR-3 in the [red-team findings](06_red_team_findings.md)). A native speaker still needs to check the Arabic and French banner lines.
- **Repeat the disclosure** when a conversation becomes a complaint or a refund request. The guidance expects reminders in complaint contexts.
- **Check accessibility.** Screen readers must announce the disclosure. Arabic must render right-to-left.
- **Keep the "AI assistant" label next to the brand name.** "Lumi Skin's AI assistant" is good; a human-sounding name on its own would not be.

### 5.2 Article 50(2): machine-readable marking of AI-generated text (open question)

**The law.** Providers of AI systems that generate synthetic audio, image, video **or text** must mark the outputs in a machine-readable format so that they can be detected as artificially generated [EU-1, Art. 50(2)]. Systems placed on the market **before 2 August 2026** have until **2 December 2026** to comply. Article 111(4) sets this date, and the Digital Omnibus added that paragraph [EU-2, Art. 111]. Exceptions cover AI that performs an assistive function for standard editing and AI that does not substantially alter the input.

**Why this is open for Lumi.** A chat reply is AI-generated text, so a plain reading puts it in scope. Law-firm summaries of the final guidelines say three things:

- the provider of the AI system stays responsible for compliance, even when the model provider marks the outputs further up the supply chain;
- the Code of Practice treats one layer of watermarking as enough for free-form text, with carve-outs for short text;
- cost alone is not an exemption [EU-8, EU-9].

We have not read those parts of the guidelines or of the Code in the original text. **Counsel should confirm:**

- whether short, one-to-one customer-service replies need marking;
- whether marking applied at the model level can be relied on, and on what contract terms.

**Practical next step (engineering + procurement).** Ask OpenRouter and each model provider in `MODEL_MAIN` and `MODEL_CHEAP`:

1. whether they mark text outputs;
2. whether they have signed the Code of Practice [EU-7];
3. what detection tool they offer.

Record the answers in the risk register, under risk R10.

### 5.3 Article 50(3) and 50(4): do not apply

- **Article 50(3), emotion recognition and biometric categorisation.** An "emotion recognition system" works "on the basis of their biometric data" (Art. 3(39)). Lumi reads only typed text. Its intent model labels the sentiment of a message (`calm`, `upset` or `angry`) so that angry customers go to a person. Text is not biometric data, so this is **not** emotion recognition under the Act. Re-check this if a voice channel is added. The P9 voice-agent project would be one example.
- **Article 50(4), deep fakes and text published to inform the public on matters of public interest.** Lumi does not create images, audio or video, and it does not publish news-type text.

### 5.4 Penalties

Breaking Article 50 can lead to fines of up to **EUR 15 million or 3% of total worldwide annual turnover**, whichever is higher. Smaller companies can get proportionate treatment. National market surveillance authorities do most of the enforcement [EU-6].

## 6. Duties that do **not** apply, and why

| Duty | Article | Why it does not apply to Lumi | What we do anyway (voluntarily) |
|---|---|---|---|
| Risk-management system | 9 | Lumi is not high-risk | A [risk register](risk_register.csv) with owners and evidence |
| Data and data governance | 10 | Lumi is not high-risk, and it does not train a model | Synthetic data only; a data inventory in the [UAE notes](05_uae_data_protection_notes.md) |
| Technical documentation | 11 | Lumi is not high-risk | A [system card](01_system_card.md) |
| Record-keeping (automatic logs) | 12 | Lumi is not high-risk | The approval audit log and model-call traces (see the [runbook](07_human_oversight_and_incident_runbook.md)) |
| Human oversight | 14 | Lumi is not high-risk | An approval queue for every refund and address change ([human-oversight design](07_human_oversight_and_incident_runbook.md)) |
| Conformity assessment, CE marking, EU database registration | 43, 48, 49 | Lumi is not high-risk | None needed |
| Deployer duties for high-risk systems, and the fundamental-rights impact assessment | 26, 27 | Lumi is not high-risk | None needed |
| Authorised representative in the EU | 22 | This duty is for providers of *high-risk* systems established outside the EU | Revisit if Lumi is ever reclassified |
| General-purpose AI model duties | 53–55 | Lumi Skin does not place a general-purpose model on the market | Keep a record of which models Lumi uses, and on which dates |
| Article 50(3) and 50(4) | 50 | No emotion recognition from biometric data, no deep fakes, no public-interest publishing | None needed |

**One duty that does apply outside Article 50: AI literacy (Art. 4).** As amended by the Omnibus, providers and deployers "shall take measures to support the development of AI literacy of their staff and other persons dealing with the operation and use of AI systems on their behalf". The article adds that this "does not require providers or deployers to guarantee any specific level of AI literacy of any individual" [EU-2, Art. 4]. **Action:** give a 30-minute briefing to every approver before go-live, and keep an attendance record. The briefing covers what Lumi can and cannot do, the common failures, and when to deny or escalate.

**Other EU law (out of scope here).** The GDPR will very likely apply to EU customers' personal data. Consumer-protection law also applies. Neither is covered in this memo.

## 7. Key dates

| Date | What happens | Source |
|---|---|---|
| 1 Aug 2024 | The AI Act enters into force | EU-1, Art. 113 |
| 2 Feb 2025 | Chapters I and II apply: the prohibitions and AI literacy | EU-2, Art. 113 |
| 2 Aug 2025 | The rules for general-purpose AI models, governance and penalties apply | EU-2, Art. 113 |
| 7 May 2026 | Council and Parliament reach a provisional agreement on the Digital Omnibus on AI | EU-4 |
| 10 Jun 2026 | Final Code of Practice on Transparency of AI-generated Content | EU-7 |
| 8 Jul 2026 | Regulation (EU) 2026/1744 (the Digital Omnibus on AI) is adopted. It is published in the Official Journal on 24 Jul 2026 (secondary source) and enters into force on 27 Jul 2026 | EU-3, EU-10 |
| 20 Jul 2026 | The Commission publishes its Article 50 guidelines | EU-5 |
| **2 Aug 2026** | **General application of the AI Act, including Article 50** | EU-2, Art. 113; EU-6 |
| 2 Dec 2026 | Article 50(2) marking deadline for systems placed on the market before 2 Aug 2026. The new prohibitions added by the Omnibus also start to apply on this date. | EU-2, Art. 111(4) and Art. 113 |
| 2 Dec 2027 | High-risk rules apply to Annex III systems (moved by the Omnibus) | EU-2, Art. 113 |
| 2 Aug 2028 | High-risk rules apply to Annex I systems (products) | EU-2, Art. 113 |

## 8. What we need from engineering before an EU launch

1. Keep the disclosure test in CI. The release is blocked if the disclosure is missing in any of the three languages.
2. Keep the page banner (now in Arabic, English and French) visible next to the chat input. Add a reminder when a conversation turns into a complaint or refund request (section 5.1). Add a test for each.
3. Write down the model IDs and the dates each one was used, and record any model change in the [system card](01_system_card.md#5-models). This was first done for the live evaluation of 8 October 2026. Every model change triggers the change rule in the runbook.
4. Collect the vendors' written answers on marking text outputs (section 5.2).
5. Keep the approval audit log and the traces for the retention period in the runbook.

## 9. Open questions for counsel

1. Do one-to-one customer-service replies need Article 50(2) marking, and can marking done by the upstream model provider be relied on?
2. P1 introduces itself as "Lumi Skin's AI assistant, not a human". If the product later gets a short persona name (P3's test prompt uses "Lumi"), is that name, together with the "AI assistant" label and the first-message disclosure, enough? Or should the name itself avoid sounding human?
3. Once Lumi Skin sells to EU consumers, does it need an EU representative for the GDPR (GDPR Art. 27)? This is a GDPR question, not an AI Act one.

---
This is not legal advice. Sources: see [sources.md](sources.md). The IDs in square brackets, such as [EU-2], point to that list.
