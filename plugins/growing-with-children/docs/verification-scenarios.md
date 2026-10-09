# Acceptance Criteria & Representative Scenarios

## Acceptance criteria
- AC-01 correct life-stage adaptation
- AC-02 correct dominant-intent routing
- AC-03 no unnecessary deep workflow for quick requests
- AC-04 adult-child mutuality
- AC-05 sensitive issue uses PK-15/IM-10 without automatic crisis labeling
- AC-06 credible high-risk indicator activates CP-01/IM-09
- AC-07 formal inductive study follows PK-16 and wait behavior
- AC-08 exact CUV quotation grounded in RM-04A/B
- AC-09 Scripture text / interpretation / application / supplemental knowledge remain distinguishable
- AC-10 visible reference fallback
- AC-11 pause/resume/revise/skip/stop honored
- AC-12 examples never override authority sources
- AC-13 no diagnosis, psychotherapy, or coercive/shaming sensitive-issue guidance
- AC-14 successful completion produces a realistic next step
- AC-15 implementation neutrality preserved

## Representative scenarios
- T-01 repeated dishonesty, school-age child
- T-02 parent guilt about teenager
- T-03 adult-child disagreement
- T-04 adolescent faith doubt
- T-05 simple Bible guidance
- T-06 formal inductive study of Romans 15:1–13
- T-07 sensitive disclosure without immediate danger
- T-08 sensitive disclosure with coercion/abuse
- T-09 15-minute teen family devotion
- T-10 PK-16 unavailable during formal-study request
- T-11 short-answer preference
- T-12 pause/resume formal study

These scenarios are specification tests, not evidence that implementation has been executed.


# Evidence contract
Run T-01–T-12 after W1. Capture selected route, actual reference reads, output, wait/transition and fallback. Also remove PK-16 in an isolated fixture, simulate PDF unavailability, and contrast sensitive-only vs coercion/abuse. Static structural PASS is not evidence of conversational behavior. Evidence state at W1: EXPECTED; runtime NOT VERIFIED.


## REQ semantic verification update
The owner supplied the Application Plugin Design Specification v1.0 artifact during W2 review. Its verbatim REQ-001–REQ-012 statements are now captured in `docs/traceability.md` and `docs/traceability.json` and mapped to implementation owners and static evidence.

Result: REQ-001–REQ-012 semantic coverage is STATICALLY VERIFIED. This does not change T-01–T-12 runtime states; they remain NOT VERIFIED until executed in an installed target runtime.
