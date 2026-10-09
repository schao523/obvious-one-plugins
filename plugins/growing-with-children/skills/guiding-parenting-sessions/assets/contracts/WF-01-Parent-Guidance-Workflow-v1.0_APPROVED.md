# WF-01 — Parent Guidance Workflow Blueprint v1.0 — APPROVED — effective packaged state

## workflow_id
WF-01

## mission_outcome
Help a Christian parent or adult caregiver identify the child's life stage and current parenting/relationship need, choose an appropriate parental role and response mode, integrate relevant biblical/parenting guidance, and leave with one context-appropriate next step while preserving safety, relationship, and age-appropriate responsibility.

## actors
- Christian parent or adult caregiver
- Child / adolescent / adult child as the subject of guidance
- External professional or emergency actor when CP-01 safety escalation is triggered

## inputs

### required
- A parenting, relationship, faith, behavior, habit, family-devotion, or sensitive-issue concern
- Enough context to determine whether ordinary parenting guidance is safe to continue

### optional
- Child age / life stage
- Concrete event or behavior
- Parent's desired type of help
- Parent emotional state
- Relevant Scripture passage
- Desired depth: quick advice / guided reflection / formal Bible study / co-design
- Existing family boundaries or responsibilities
- Prior attempts and outcomes

## states

### S0 — START
- **kind:** start
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **purpose:** Receive the user's initial concern and identify whether the request is already sufficiently clear.
- **transitions:**
  - `clear_and_non_sensitive` → S2
  - `life_stage_or_context_missing_and_material` → S1
  - `sensitive_issue_detected` → S-SENS
  - `credible_safety_indicator` → S-SAFE
  - `user_stops` → E-STOP

### S1 — Context & Life-stage Triage
- **kind:** wait
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** yes, after asking one focused consequential question
- **purpose:** Resolve only the missing context that materially changes advice.
- **transitions:**
  - `required_context_received` → S2
  - `user_declines_optional_detail_but_safe_generic_guidance_possible` → S2
  - `credible_safety_indicator` → S-SAFE
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F1

### S2 — Need & Role Classification
- **kind:** action
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no unless ambiguity materially affects routing
- **purpose:** Classify the dominant need and select the logical response path.
- **transitions:**
  - `goal_habit_character` → S-COACH
  - `concrete_parenting_problem` → S-CONSULT
  - `parent_emotion_guilt_anxiety_inner_struggle` → S-MENTOR
  - `bible_scripture_or_bible_study` → S-TUTOR
  - `family_devotion_or_activity` → S-PARTNER
  - `multiple_material_needs` → S-MULTI
  - `sensitive_issue_detected` → S-SENS
  - `ambiguity_material` → S2Q
  - `credible_safety_indicator` → S-SAFE
  - `failure` → F2

### S2Q — Routing Clarification
- **kind:** wait
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** yes
- **purpose:** Ask one question to resolve routing ambiguity.
- **transitions:**
  - `clarified` → S2
  - `user_requests_quick_advice` → S-CONSULT
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F2

### S-COACH — Guided Growth Coaching
- **kind:** action
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** step-dependent
- **modules:** IM-03 + IM-08 + IM-09 as applicable
- **transitions:**
  - `guided_step_requires_user_input` → S-COACH-WAIT
  - `coaching_complete` → S-NEXT
  - `parent_emotion_becomes_primary` → S-MENTOR
  - `scripture_study_requested` → S-TUTOR
  - `sensitive_issue_detected` → S-SENS
  - `credible_safety_indicator` → S-SAFE
  - `failure` → F3

### S-COACH-WAIT — Coaching Wait
- **kind:** wait
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** yes
- **transitions:**
  - `user_answered` → S-COACH
  - `user_requests_direct_advice` → S-CONSULT
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F3

### S-CONSULT — Practical Parenting Advice
- **kind:** action
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no unless one material ambiguity remains
- **modules:** IM-04 + IM-08 + IM-09 as applicable
- **transitions:**
  - `advice_complete` → S-NEXT
  - `needs_one_clarification` → S1
  - `parent_reflection_needed_and_user_wants_depth` → S-MENTOR
  - `bible_guidance_requested` → S-TUTOR
  - `sensitive_issue_detected` → S-SENS
  - `credible_safety_indicator` → S-SAFE
  - `failure` → F4

### S-MENTOR — Parent Reflection & Pastoral Support
- **kind:** action
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** step-dependent
- **modules:** IM-05 + IM-08 + IM-09 as applicable
- **transitions:**
  - `reflection_question_asked` → S-MENTOR-WAIT
  - `reflection_complete` → S-NEXT
  - `user_exits_depth_for_practical_advice` → S-CONSULT
  - `bible_guidance_requested` → S-TUTOR
  - `credible_safety_indicator` → S-SAFE
  - `failure` → F5

### S-MENTOR-WAIT — Reflection Wait
- **kind:** wait
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** yes
- **transitions:**
  - `user_answered` → S-MENTOR
  - `user_requests_quick_advice` → S-CONSULT
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F5

### S-TUTOR — Biblical Guidance / Bible Study Routing
- **kind:** action
- **interaction_protocol:** UIP-03 Socratic-Study for formal study; UIP-02 for simple guidance
- **wait:** mode-dependent
- **modules:** IM-06 + IM-08 + IM-09 as applicable
- **transitions:**
  - `simple_bible_guidance` → S-TUTOR-DIRECT
  - `formal_inductive_study` → S-TUTOR-STUDY
  - `credible_safety_indicator` → S-SAFE
  - `failure` → F6

### S-TUTOR-DIRECT — Simple Biblical Guidance
- **kind:** action
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **transitions:**
  - `guidance_complete` → S-NEXT
  - `user_requests_formal_study` → S-TUTOR-STUDY
  - `failure` → F6

### S-TUTOR-STUDY — Formal Inductive Bible Study
- **kind:** action
- **interaction_protocol:** UIP-03 Socratic-Study
- **wait:** yes at each interactive step
- **transitions:**
  - `step_question_asked` → S-TUTOR-WAIT
  - `all_required_steps_complete` → S-NEXT
  - `user_requests_direct_explanation` → S-TUTOR-DIRECT
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F6

### S-TUTOR-WAIT — Bible Study Wait
- **kind:** wait
- **interaction_protocol:** UIP-03 Socratic-Study
- **wait:** yes
- **transitions:**
  - `user_answered` → S-TUTOR-STUDY
  - `user_requests_hint` → S-TUTOR-STUDY
  - `user_requests_direct_explanation` → S-TUTOR-DIRECT
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F6

### S-PARTNER — Family Devotion & Activity Design
- **kind:** action
- **interaction_protocol:** UIP-04 Co-Creative
- **wait:** depends on whether key design choices are missing
- **modules:** IM-07 + IM-08 + IM-09 as applicable
- **transitions:**
  - `key_design_choice_missing` → S-PARTNER-WAIT
  - `activity_complete` → S-NEXT
  - `bible_study_requested` → S-TUTOR
  - `credible_safety_indicator` → S-SAFE
  - `failure` → F7

### S-PARTNER-WAIT — Co-design Wait
- **kind:** wait
- **interaction_protocol:** UIP-04 Co-Creative
- **wait:** yes
- **transitions:**
  - `user_selected_or_revised` → S-PARTNER
  - `user_accepts_default_option` → S-PARTNER
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F7

### S-MULTI — Multi-need Sequencing
- **kind:** action
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no unless sequence choice is consequential
- **purpose:** Sequence only the layers actually needed.
- **default sequence:** Mentor → Coach/Consultant → Tutor/Partner
- **transitions:**
  - `emotion_first` → S-MENTOR
  - `practical_first_requested` → S-CONSULT
  - `coaching_first` → S-COACH
  - `bible_first_requested_and_safe` → S-TUTOR
  - `sensitive_issue_detected` → S-SENS
  - `failure` → F8

### S-SENS — Sensitive-Issue Discernment
- **kind:** action
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** step-dependent
- **modules:** IM-10 + IM-09 + IM-08
- **transitions:**
  - `safety_unclear_or_triggered` → S-SAFE
  - `clarification_question_needed` → S-SENS-WAIT
  - `relationship_guidance_sufficient` → S-NEXT
  - `practical_parenting_needed` → S-CONSULT
  - `parent_reflection_needed` → S-MENTOR
  - `biblical_guidance_requested` → S-TUTOR
  - `adult_child_case` → S-CONSULT
  - `failure` → F9

### S-SENS-WAIT — Sensitive-Issue Wait
- **kind:** wait
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** yes
- **transitions:**
  - `user_answered` → S-SENS
  - `user_declines_nonessential_detail` → S-SENS
  - `safety_question_required` → S-SAFE
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F9

### S-SAFE — Safety & Escalation
- **kind:** action
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** only if one minimum safety-critical question is required
- **modules:** IM-09; CP-01 governs
- **transitions:**
  - `one_safety_question_required` → S-SAFE-WAIT
  - `immediate_or_serious_risk_confirmed` → E-SAFETY
  - `risk_not_immediate_and_parenting_can_resume` → S-SENS
  - `risk_ruled_out_and_non_sensitive` → S2
  - `failure` → F10

### S-SAFE-WAIT — Safety Clarification Wait
- **kind:** wait
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** yes
- **transitions:**
  - `risk_confirmed` → E-SAFETY
  - `risk_not_immediate` → S-SENS
  - `cannot_determine_but_credible_risk_remains` → E-SAFETY
  - `user_stops` → E-STOP
  - `failure` → F10

### S-NEXT — Next-step Consolidation
- **kind:** action
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **purpose:** Summarize the current understanding and identify one realistic next step.
- **transitions:**
  - `mission_outcome_achieved` → E-SUCCESS
  - `user_requests_revision` → S2
  - `user_requests_another_layer` → S-MULTI
  - `user_pauses` → E-PAUSE
  - `user_stops` → E-STOP
  - `failure` → F11

### F1 — Context Triage Failure
- **kind:** failure
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no
- **transitions:**
  - `retry` → S1
  - `continue_with_safe_generic_guidance` → S2
  - `stop` → E-STOP

### F2 — Routing Failure
- **kind:** failure
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no
- **transitions:**
  - `retry` → S2Q
  - `default_to_practical_advice` → S-CONSULT
  - `stop` → E-STOP

### F3 — Coaching Failure
- **kind:** failure
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no
- **transitions:** {`retry` → S-COACH, `switch_to_direct_advice` → S-CONSULT, `stop` → E-STOP}

### F4 — Advice Failure
- **kind:** failure
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **transitions:** {`retry_after_clarification` → S1, `stop` → E-STOP}

### F5 — Reflection Failure
- **kind:** failure
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no
- **transitions:** {`retry` → S-MENTOR, `switch_to_practical_advice` → S-CONSULT, `stop` → E-STOP}

### F6 — Bible Guidance Failure
- **kind:** failure
- **interaction_protocol:** UIP-03 Socratic-Study
- **wait:** no
- **transitions:** {`retry` → S-TUTOR, `downgrade_to_simple_guidance_if_text_available` → S-TUTOR-DIRECT, `stop` → E-STOP}

### F7 — Co-design Failure
- **kind:** failure
- **interaction_protocol:** UIP-04 Co-Creative
- **wait:** no
- **transitions:** {`retry` → S-PARTNER, `use_simple_default_activity` → S-PARTNER, `stop` → E-STOP}

### F8 — Multi-need Sequencing Failure
- **kind:** failure
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no
- **transitions:** {`choose_one_primary_need` → S2Q, `stop` → E-STOP}

### F9 — Sensitive-Issue Failure
- **kind:** failure
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no
- **transitions:** {`retry_with_minimum_clarification` → S-SENS-WAIT, `safety_concern` → S-SAFE, `stop` → E-STOP}

### F10 — Safety Handling Failure
- **kind:** failure
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **transitions:** {`fail_safe_escalation` → E-SAFETY, `stop` → E-STOP}

### F11 — Consolidation Failure
- **kind:** failure
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **transitions:** {`retry` → S-NEXT, `stop` → E-STOP}

### E-SUCCESS — Successful Completion
- **kind:** end
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **transitions:** {}

### E-SAFETY — Safety Escalation Terminal
- **kind:** end
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **transitions:** {}

### E-PAUSE — Paused
- **kind:** end
- **interaction_protocol:** UIP-01 Guided-Step
- **wait:** no
- **transitions:** {}

### E-STOP — User Stopped
- **kind:** end
- **interaction_protocol:** UIP-02 Direct-Advisory
- **wait:** no
- **transitions:** {}

## start
S0

## terminal_states
- E-SUCCESS
- E-SAFETY
- E-PAUSE
- E-STOP

## successful_terminal_states
- E-SUCCESS

## hitl_checkpoints
These are conditional rather than universal across every path:
- S1 when required context is missing
- S2Q when routing ambiguity is material
- S-COACH-WAIT for interactive coaching
- S-MENTOR-WAIT for reflection
- S-TUTOR-WAIT for formal Bible study
- S-PARTNER-WAIT when co-design choice is required
- S-SENS-WAIT when sensitive-issue clarification is necessary
- S-SAFE-WAIT when one minimum safety-critical question is necessary

No successful path may bypass a wait state that is required by the selected route.

## completion_criteria
- The child's relevant life stage is known or safely treated as non-consequential.
- The dominant parenting/relationship need has been classified sufficiently for the response.
- Any credible safety issue has been triaged before ordinary coaching continues.
- The response mode is appropriate to both the issue and life stage.
- Relevant required references have been consulted or a defined fallback has been used.
- The parent leaves with at least one clear, context-appropriate next step.
- The response does not require immediate agreement or forced disclosure as proof of success.
