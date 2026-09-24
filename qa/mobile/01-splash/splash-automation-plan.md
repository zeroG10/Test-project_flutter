# Automation plan — Splash (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/01-splash/splash-checklist.md`
> (15 items, `CHK-SPL-001…015`). Reviewed copy for the module; the **Selected CHK IDs** table is the contract for
> `prompts/mobile/03` (test cases). Date: 2026-09-23. Owner: mykola.zhuchenko. **Status: draft — waits for the owner.**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| App build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Feature code | `SPL` |
| Scope decision | breadth (owner, 2026-09-23): screens, transitions, happy path, key validations |
| Oracle model | accepted production baseline; SRS §3.1.0 + checklist explain; Figma `Splash & Wellcome` 2451:82537 and `Spalsh animation` 2451:83867 decide the visual layer |

## Step 0 — Input quality

**Overall: Medium.** Stable IDs, single-assertion wording, SRS §3.1.0 with four FRs, Figma frames for the splash
and its animation. Read-only look at the app code (`splash_page.dart`, `auth_bloc.dart`) and at Figma explains
what the live app does. Gaps: three items contradict both the design and the app (static logo, white background,
"navigates to Login") — D-SPL-1…3 in [splash-questions.md](splash-questions.md); one item needs a time budget nobody
has set (CHK-SPL-014). D-SPL-1…4 were **accepted by the owner on 2026-09-23** (the app is right). The splash has
**no labelled element**, so its own checks need a pixel oracle.

## Step 1 — Readiness: **Ready with conditions**

Routing after the splash (Welcome / Jobs list) is fully text-locatable and already exercised by the Auth suite. The
splash itself is only observable through pixels (brand colour `#782A2A`, the white logo) and through the absence of
elements in the tree — both need a short recon to confirm the timing: without a session the splash lasts ~2.8 s
(2.0 s animation + 0.8 s transition, code), with a session the app leaves it after ~0.8 s.

## Step 2 — Approach: **UI only**, API only for the revoked-session setup

## Step 3–4 — Candidate matrix (all 15 items)

| CHK ID | Scenario (short) | Automation Level | ROI | Stability | Risk | Automation Status | Priority | Tags | TC | Reason / blocker |
|---|---|---|---|---|---|---|---|---|---|---|
| CHK-SPL-001 | splash shown immediately after launch | E2E UI | M | M | M | Medium Candidate | P0 | @smoke | TC-SPL-001 | first captured frame is the splash (pixels); timing to confirm in recon |
| CHK-SPL-002 | full-screen, white background | E2E UI | M | M | L | Medium Candidate | P1 | @regression | TC-SPL-001 | app and Figma use the brand colour, not white (D-SPL-2, accepted) — asserted as the app does it |
| CHK-SPL-003 | logo centred vertically and horizontally | E2E UI | M | M | L | Medium Candidate | P1 | @regression | TC-SPL-001 | logo unlabelled → centre of the light blob on the brand background (pixels, ±2 % of the screen) |
| CHK-SPL-004 | logo static, no animation / loading indicator | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | the logo **is** animated in the app and in Figma (`Spalsh animation`) — D-SPL-1, accepted → **Skipped** with that reason |
| CHK-SPL-005 | no texts, buttons, links or inputs | E2E UI | M | M | M | Medium Candidate | P1 | @regression | TC-SPL-001 | tree holds no text / button / field while the splash colour is on screen |
| CHK-SPL-006 | system status bar visible | Manual only | L | L | L | Manual Only | — | @manual-only | — | the status bar is drawn by iOS outside the app's tree; visual check |
| CHK-SPL-007 | no interaction possible (taps, swipes, back) | E2E UI | M | L | M | Medium Candidate | P2 | @regression | TC-SPL-001 | tap + edge swipe during the splash change nothing; long press excluded (dev-flavour debug screen, D-SPL-4) |
| CHK-SPL-008 | existing session validated in the background | E2E UI | H | H | H | Good Candidate | P1 | @regression @critical | TC-SPL-002 | proven by outcome: valid session → Jobs list without Welcome |
| CHK-SPL-009 | authentication token status verified | E2E UI + API setup | H | M | H | Needs API Support | P1 | @regression @critical | TC-SPL-003 | proven by outcome: account deleted on the server → next launch ends on Welcome |
| CHK-SPL-010 | configuration and metadata loaded | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | not observable from the UI; no oracle |
| CHK-SPL-011 | no session → Login screen | E2E UI | H | H | H | Good Candidate | P0 | @smoke | TC-SPL-001 | the app opens **Welcome** (D-SPL-3, accepted; SRS FR-WEL-03 says the same) |
| CHK-SPL-012 | valid session → Jobs list / Calendar | E2E UI | H | H | H | Good Candidate | P1 | @regression @critical | TC-SPL-002 | text locators; overlaps TC-AUTH-003 (see Step 11) |
| CHK-SPL-013 | transition without visible delays or artifacts | Manual only | L | L | L | Manual Only | — | @manual-only | — | subjective |
| CHK-SPL-014 | splash shown only as long as initialization needs | E2E UI | M | M | L | Medium Candidate | P3 | @regression | — | **manual** (owner, 2026-09-24); the debug build starts in ~9 s (recon 4) — the measured duration is reported as information only |
| CHK-SPL-015 | slow initialization handled without glitches | Not applicable yet | L | L | L | Not Recommended Now | — | — | — | no network throttling on the iOS simulator; revisit on Android |

## Step 5 — Best first candidates

1. TC-SPL-001 — cold start without a session: the one screen every user sees first; P0 smoke.
2. TC-SPL-002 — session hand-over to the Jobs list; cheap on top of the session fixture.
3. TC-SPL-003 — revoked session ends on Welcome: the only splash check with a security angle, and it also closes
   gap MISS-10 of the Auth coverage review.

## Step 5b — Selected CHK IDs (handoff to prompts/mobile/03)

**9 of 15 → 3 test cases.**

| CHK ID | Automation Level | Priority | Automation Status | Blockers to clear before Prompt 07 | Note |
|---|---|---|---|---|---|
| CHK-SPL-001 | E2E UI | P0 | Medium Candidate | recon: can the first frames be captured within the splash window | → TC-SPL-001 |
| CHK-SPL-002 | E2E UI | P1 | Medium Candidate | — (D-SPL-2 accepted) | → TC-SPL-001 |
| CHK-SPL-003 | E2E UI | P1 | Medium Candidate | pixel helper for the logo blob | → TC-SPL-001 |
| CHK-SPL-005 | E2E UI | P1 | Medium Candidate | recon: tree during the splash | → TC-SPL-001 |
| CHK-SPL-007 | E2E UI | P2 | Medium Candidate | recon: actions land inside the splash window | → TC-SPL-001 |
| CHK-SPL-008 | E2E UI | P1 | Good Candidate | — | → TC-SPL-002 |
| CHK-SPL-009 | E2E UI + API setup | P1 | Needs API Support | — (owner go 2026-09-24); red today: BUG-SPL-001 | → TC-SPL-003 |
| CHK-SPL-011 | E2E UI | P0 | Good Candidate | — (D-SPL-3 accepted) | → TC-SPL-001 |
| CHK-SPL-012 | E2E UI | P1 | Good Candidate | — | → TC-SPL-002 |

## Step 6 — Manual-only

| CHK ID | Scenario | Reason | Revisit? |
|---|---|---|---|
| CHK-SPL-006 | status bar visible | drawn by iOS outside the app tree | if visual regression is added |
| CHK-SPL-013 | transition without delays / artifacts | subjective | no |

Skipped: CHK-SPL-004 (the logo is animated by design, D-SPL-1). Not recommended now: CHK-SPL-010 (not observable), CHK-SPL-015 (no network
throttling on iOS). Manual by the owner's decision: CHK-SPL-014 (debug-build timing is not representative).

## Step 7 — API support

| CHK / TC | Scenario | API action | Endpoint | Priority | Notes |
|---|---|---|---|---|---|
| TC-SPL-003 | revoked session | delete the freshly registered user while the app is closed | `GET /technician?search=<email>` → `DELETE /user/full-delete/{id}` — same calls as TC-AUTH-013 cleanup (verified 2026-09-23) | P1 | the user is registered through the UI first (no API returns a session for the app) |

## Step 8 — Stable selectors

The splash has none: no text, no id (TD-ALL-001). Oracles: **pixels** (brand colour share of the screen, the logo
blob's centre — `helpers/pixels.py` gets two small functions) and **the tree** (count of text / button / field
elements). Afterwards everything is text: `welcome.root`, `login.root`, `jobs-list.root` already exist.

## Step 9 — Test data

| TC | Data | Source | Reusable | Cleanup |
|---|---|---|---|---|
| TC-SPL-001 | none | — | — | — |
| TC-SPL-002 | test technician session | `ui_login` fixture (existing account) | yes | reset app data after |
| TC-SPL-003 | new user `qa-auto+<ts>@example.com`, `+1 202 555 01xx` | generated, registered through the UI | no | the test itself deletes it through the API; teardown verifies it is gone |

## Step 10 — Authentication & session

| Role | TCs | Login method | Notes |
|---|---|---|---|
| none (logged out) | TC-SPL-001 | app data reset | — |
| Field Technician | TC-SPL-002 | `ui_login` fixture (once per run) | the relaunch keeps the session |
| new technician | TC-SPL-003 | UI registration in setup (as TC-AUTH-013) | one extra OTP per run (DEV code) |

## Step 11 — Isolation

| TC | Independent | Creates data | Cleanup | Setup / teardown |
|---|---|---|---|---|
| TC-SPL-001 | yes | no | no | logged-out cold start |
| TC-SPL-002 | yes | session | app reset after | session fixture, relaunch |
| TC-SPL-003 | yes | **user** | **API delete (by the test) + verify in `finally`** | registration in setup |

**Overlap:** TC-SPL-002 and TC-AUTH-003 both relaunch with a session. Recommendation: keep both — each module's
report must stand on its own and the cost is one relaunch (~15 s). The owner can retire one.

## Step 12 — Plan

- Tests: `automation/mobile/tests/shared/test_splash.py` (`@pytest.mark.shared`).
- Screen map: `screens/splash_map.py` (no locators — the screen is decided by pixels and by the tree); page
  `pages/splash_page.py` with `expect_shown()`, `expect_logo_centred()`, `expect_no_interactive_elements()`,
  `wait_until_gone()`. Pixel helpers in `helpers/pixels.py`: colour share of a region, bounding box of a light blob.
- Fixtures: existing `logged_out_app`, `ui_login`, `new_user`; a small `registered_new_user` fixture (UI
  registration via the existing `RegistrationPage` / `OtpPage` methods).
- Order: TC-SPL-001 → TC-SPL-002 → TC-SPL-003.
- Estimate: ~6–8 h incl. recon and the pixel helpers. Maintenance risk: **Medium** — the pixel thresholds depend on
  the brand colour and the logo asset.

## Step 13 — Runtime notes

Same rules as the Auth plan (maps only, explicit waits, no retries, CHK tags, evidence). Specific here: the
first-frame capture must not wait for app idle (the splash animation keeps the app "busy") — the recon decides
between a screenshot right after launch and the first frames of the video that is recorded anyway.

## Step 14 — CI readiness

As the Auth plan (macOS runner for iOS; serial). Timing checks are sensitive to a slow CI machine — the splash
window is ~2.8 s; the TC turns **Blocked** (not Failed, not Passed) when it cannot observe the splash in time.

## Step 15 — Risks

| Category | Risk | Impact | Action | Owner |
|---|---|---|---|---|
| Technical | the splash window is shorter than Appium's first screenshot | TC-SPL-001 cannot see the splash | recon first; fall back to video frames | Automation QA |
| Technical | pixel thresholds drift with a new logo or colour | false red | thresholds live in one place, calibrated in recon | Automation QA |
| Data | a registered user left on DEV if the test dies before the delete | clutter | `finally` deletes by the generated email, as TC-AUTH-013 | Automation QA |
| Process | three items contradicted the app (D-SPL-1…3) | wrong expectations | **resolved** — the owner accepted the app, 2026-09-23 | Owner |

## Step 16 — Final recommendation

Start after a short recon (one cold start with and one without a session, video on) and the owner's word on
TC-SPL-003 creating a user (Q-SPL-2). D-SPL-1…4 are accepted. **First sprint scope:** TC-SPL-001…003 (9 CHK IDs).
