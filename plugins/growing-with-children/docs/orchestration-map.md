# WF-01 implementation orchestration map

Effective implementation state: APPROVED W1 candidate mapping. This document does not change WF-01 behavior.

| Transition / state | Implementation owner | Observable behavior |
|---|---|---|
| S0 intake | guiding-parenting-sessions | Identify presenting concern and minimum consequential context. |
| S1 life-stage triage | guiding-parenting-sessions | Resolve stage only when material; consult PK-07/08/09/10 as applicable. |
| S1 safety precedence | guiding-parenting-sessions | Credible serious risk activates CP-01/IM-09 before ordinary role routing. |
| S1 sensitive triage | guiding-parenting-sessions + coaching-parenting-and-sensitive-conversations | Sensitive-but-not-high-risk concerns use PK-15/IM-10 without automatic crisis labeling. |
| S2 role selection | guiding-parenting-sessions | Route to Coach, Consultant, Mentor, Tutor, or Partner according to dominant need. |
| Coach ↔ Consultant | coaching-parenting-and-sensitive-conversations | Shift between guided growth coaching and direct practical advice when user need changes. |
| Mentor → Consultant/Coach | supporting-parent-reflection → coaching-parenting-and-sensitive-conversations | Move from reflection to action when the user's dominant need changes. |
| Tutor simple → formal | guiding-biblical-study | Formal mode activates PK-16 ten-step sequence and waits; simple mode stays lightweight. |
| Partner → Tutor | designing-family-devotions → guiding-biblical-study | Bible explanation, exact CUV quotation, or formal study hands to Tutor owner. |
| Any route → safety | guiding-parenting-sessions | CP-01/IM-09 overrides ordinary path. |
| Sensitive → practical/reflection/biblical | guiding-parenting-sessions | After PK-15 triage, route according to dominant need if no high-risk override. |
| Pause/resume/stop/revise/skip | guiding-parenting-sessions, honored by all Skills | Preserve conversational summary and current study step; resume states saved state; stop ends; revise invalidates dependent assumptions; skip is honored where allowed. |
| Failure/retry/fallback | owning Skill, coordinated by guiding-parenting-sessions | Use declared Skill-local fallback; never silently substitute model memory for required authority. |

Exact CUV retrieval is physically owned by `guiding-biblical-study`, which contains RM-04A/B. Other Skills hand off rather than relying on redundant PDF copies.
