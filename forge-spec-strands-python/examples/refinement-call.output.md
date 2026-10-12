# Epic: Enable 'Retry what I got wrong' for Practice BET (reading and listening)

**Goal:** Let learners retry only the questions they missed in reading and listening Practice BETs for targeted practice without affecting official scores.
**Source:** Refinement call, 21 min. References in [brackets] are transcript timestamps.

## Open questions (resolve before sizing)

1. **Which users/tiers get the feature?** PM needs to check whether this is for all users or only the paid tier. Owner: Product manager (PM). [00:09:02, 00:09:10]
2. **Analytics event timing and schema: should the per-retry event fire on start or on completion, and what is the exact payload and event name?** TL will ensure analytics gets attempt number and how many were still wrong, but the trigger and schema were not specified. [00:05:50]
3. **How is the retry attempt number defined and scoped?** Does the attempt number reset per original Practice BET result session, per user per test, or globally? [00:05:50]
4. **Exact copy when there are zero wrong answers** PM suggested a congratulatory line; confirm final text and tone. [00:01:49]
5. **Localization of button copy** Plural/singular strings were discussed in English; confirm localization approach and translations timeline. [00:12:12, 00:12:38]
6. **Accessibility requirements for retry results** Confirm screen-reader announcements, focus order, and how explanations and correctness are conveyed accessibly.
7. **Data retention and privacy for retry attempt records and analytics** Define how long retry rows and events are kept and whether any PII is included.
8. **Should the count in the Retry button on subsequent loops reflect only remaining incorrect items (current default) or the original incorrect count?** The call implies it updates, but this was not explicitly confirmed. [00:01:31, 00:05:12]

## Stories

### 1. Show Retry CTA on the result screen with correct count and copy

As a learner who has just finished a reading or listening Practice BET,
I want a button to retry only the questions I got wrong with the correct count,
so that I can focus my practice on my mistakes.

**Acceptance criteria**

- Given the result screen of a reading or listening Practice BET and more than one question was answered incorrectly in the attempt,
  when the results are shown,
  then a primary action button labeled "Retry the N you missed" is displayed where N is the count of incorrect questions. [00:00:15, 00:00:58, 00:01:31, 00:07:28, 00:07:40]
- Given the result screen of a reading or listening Practice BET and exactly one question was answered incorrectly in the attempt,
  when the results are shown,
  then a primary action button labeled "Retry the one you missed" is displayed. [00:12:38, 00:12:12]
- Given the result screen of a reading or listening Practice BET and no questions were answered incorrectly in the attempt,
  when the results are shown,
  then no Retry button is displayed. [00:01:44, 00:01:49]
- Given the result screen shows the Retry button,
  then "Retake test" is available as a text link rather than a primary button. [00:07:28, 00:07:40]

### 2. Limit feature to reading and listening only

As a learner who has finished a Practice BET in any skill,
I want the retry-wrong-answers option only where right or wrong applies,
so that the UI reflects the nature of each skill.

**Acceptance criteria**

- Given the result screen of a speaking or writing Practice BET,
  when the results are shown,
  then no Retry-what-you-missed option is displayed. [00:00:41, 00:00:58]
- Given the result screen of a reading or listening Practice BET and there are incorrect answers,
  when the results are shown,
  then the Retry-what-you-missed option is displayed per the button rules. [00:00:58, 00:00:15]

### 3. Run a retry session with only missed items, shuffled options, and no timer

As a learner starting a retry from the result screen,
I want to answer only the questions I got wrong, with shuffled options and no timer,
so that I can relearn without memorizing positions or feeling time pressure.

**Acceptance criteria**

- Given a learner starts a retry from a result screen that shows missed items,
  then the retry session contains exactly the questions that were answered incorrectly in the immediately preceding attempt. [00:00:15, 00:05:12]
- Given a multiple-choice question is presented during a retry session,
  then its answer options are presented shuffled. [00:02:40, 00:02:52, 00:03:05]
- Given a retry session is in progress,
  then no countdown timer is shown and the session is not timed. [00:08:20, 00:08:31]

### 4. Show post-retry feedback with correctness and explanations where available

As a learner who has completed a retry attempt,
I want to see which questions I fixed and the correct answers (plus explanations where available) for those still wrong,
so that I can learn from my mistakes.

**Acceptance criteria**

- Given a retry attempt has been submitted,
  then the system shows which questions are now correct. [00:03:30, 00:03:41]
- Given a retry attempt has been submitted,
  then for each question still incorrect, the correct answer is shown. [00:03:41]
- Given a retry attempt has been submitted and an explanation exists for a still-incorrect question,
  then the explanation is displayed; if no explanation exists, only the correct answer is shown. [00:04:10, 00:04:22]
- Given a retry session is in progress,
  then the system does not reveal correct answers before submission. [00:03:30, 00:03:41]

### 5. Allow repeated retries until all correct; no cap; no resume of in-progress

As a learner practicing until all items are correct,
I want to keep retrying remaining incorrect items or stop at any time,
so that I can reach full correctness at my pace.

**Acceptance criteria**

- Given there are still incorrect items after a retry attempt completes,
  when the result screen is shown,
  then the Retry button is available with the updated count of remaining incorrect items. [00:05:12, 00:01:31]
- Given there are no incorrect items remaining after a retry attempt completes,
  when the result screen is shown,
  then the Retry button is not displayed. [00:05:12, 00:01:49]
- There is no cap on the number of retry attempts. [00:05:36, 00:05:50]
- Given a retry is in progress and the learner closes the app or leaves the session,
  when they return to the result screen,
  then the in-progress retry cannot be resumed and they can start a new retry. [00:10:30, 00:10:39]

### 6. Keep Practice BET and Summative scores unchanged by retries

As a learner concerned about my official scores,
I want my practice retries not to alter recorded Practice BET or Summative scores,
so that my results remain accurate.

**Acceptance criteria**

- Given a Practice BET attempt has a recorded score,
  when any number of retries are completed,
  then the recorded Practice BET score is unchanged. [00:02:05, 00:02:16]
- Retry attempts do not alter any Summative score. [00:02:05, 00:02:16]

### 7. Capture analytics and persist retry attempts; do not show in teacher dashboards (this release)

As a product analyst tracking usage,
I want an event per retry attempt with attempt number and remaining-wrong count, and persisted rows per attempt,
so that we can understand engagement and enable future reporting.

**Acceptance criteria**

- Given a retry attempt occurs,
  then an analytics event is captured for that attempt that includes the attempt number and how many questions were still wrong. [00:05:50]
- Each retry attempt is persisted as data (rows) to support future reporting. [00:05:25, 00:11:27]
- Retry attempts do not appear in the teacher dashboard in this release. [00:11:15, 00:11:27]

### 8. Match connectivity behavior to the normal Practice BET

As a learner using the app with patchy connectivity,
I want the retry feature to follow the same online/offline requirements as the normal test,
so that the experience is consistent.

**Acceptance criteria**

- The retry feature requires a network connection if the normal Practice BET does and behaves the same when offline. [00:09:45, 00:09:55]

## Assumptions (not stated in the source; confirm or correct)

- The count N in the Retry button reflects the number of items currently incorrect (from the immediately preceding attempt: initial test or last retry).
- Attempt numbering for analytics and persisted rows restarts from 1 for the first retry launched from a given Practice BET result screen unless decided otherwise.
- Shuffling applies to the order of answer options only; the set of questions and their order are unchanged unless otherwise specified. [00:02:40, 00:02:52, 00:03:05]
- No timer means there is no countdown UI and no server-side time limit specific to retries beyond any general session expiration. [00:08:20, 00:08:31]
- Retry attempt data is stored in a location accessible to future reporting, even though it is not yet surfaced in teacher dashboards. [00:11:27]
- Closing the app or losing connectivity during a retry abandons that attempt without partial saving or resume, consistent with "Don't build resume". [00:10:39]

## Out of scope (raised and parked)

- Applying this feature to Speaking and Writing skills. [00:00:58]
- Letting learners retry questions they got right but were slow to answer (>60 seconds). [00:06:30, 00:06:44]
- Showing retries in the teacher dashboard in this release. [00:11:15, 00:11:27]
- Resuming an in-progress retry after app close or navigation away. [00:10:39]
