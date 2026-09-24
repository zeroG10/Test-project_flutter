# qa/mobile — module index

One folder per module: `qa/mobile/<NN-module>/<module>-<artifact>.md` ([qa/README.md](../README.md)).
`NN` follows the mobile SRS order; the slug and its code are registered in
`qa/shared/feature-codes.md` **before** the first artifact is written. Web and mobile
checklists of the same feature share the code (they sync to separate Sheets).

Stage legend: intake → analysed → checklist → candidates → test cases → automated → traced.

| # | Module | Code | Checks | Figma node | Platforms | Stage | Notes |
|---|---|---|---|---|---|---|---|
| 01 | `splash` | `SPL` | 15 | `2451:82537` | android · ios · tablet | traced (iOS) | Splash screen — 3 тести (3 TC); 8 Passed, 1 Failed (BUG-SPL-001); D-SPL-1…4 |
| 02 | `authentication` | `AUTH` | 126 | `3191:12921`, `3608:11989` | android · ios · tablet | traced (iOS) | Welcome + Registration + Phone/email verification + Login — 31 тест, RTM + рев'ю покриття |
| 03 | `order-list` | `ORDL` | 70 | `2451:82604` | android · ios · tablet | traced (iOS) | Jobs list + weekly calendar + job links — 16 тестів (15 TC); 46 Passed, 4 Failed (BUG-ORDL-001…003), 2 Blocked (iOS-симулятор); D-ORDL-1…12 |
| 04 | `order-details` | `ORDD` | 89 | `2451:82657` | android · ios · tablet | traced (iOS) | Order details + Attachments — 9 тестів; разом з перевірками check-in у модулі 05: 55 Passed, 1 Blocked (телефон PF — обмеження симулятора) |
| 05 | `check-in-out` | `CHIO` | 41 (+25 ORDD) | `2451:83073` | android · ios · tablet | traced (iOS) | Check-In / Check-Out — 9 тестів; 25 CHIO Passed (+ CHK-ORDD 024…047 частково); перемикач підробленої локації для потоків, захист — окремий тест (Q-CHIO-5) |
| 06 | `order-progress` | `ORDP` | 42 | `2451:82704` | android · ios · tablet | traced (iOS) | Order details — In progress — 6 тестів (6 TC); 17 Passed, 1 Blocked (телефон PF — обмеження симулятора); здача → 07; Q-ORDP-4 (таймер) прийнято як є |
| 07 | `submit-deliverables` | `DLV` | 33 | `<node-id>` | android · ios · tablet | intake | Submit Deliverables |
| 08 | `survey` | `SRV` | 40 (+17 запропоновано) | `4009:12410` | android · ios · tablet | candidates (draft) | Survey screen: план 46 CHK → 16 TC (8 опитувань + фото + порожнє + після здачі); таблиці логіки й Q-SRV-1…5 чекають власника; офлайн → етап Android |
| 09 | `photo-report` | `PHR` | 54 | `<node-id>` | android · ios · tablet | intake | Photo report screen |
| 10 | `notes` | `NOTE` | 52 | `<node-id>` | android · ios · tablet | intake | Notes screen |
| 11 | `notifications` | `NOTIF` | 31 | `<node-id>` | android · ios · tablet | intake | Notifications screen |
| 12 | `profile` | `PRF` | 35 | `<node-id>` | android · ios · tablet | intake | Profile screen |
| | **разом** | | **625** | | | | Google Sheet: `Working_Regression Check-list_Concert Technologies– Flutter App` |

Platform column: which OS the module is verified on (`android`, `ios`, or both). A Flutter app
is still `android · ios` — Flutter is an app kind (`APP_KIND=flutter`), not a platform.

## Coverage model per module (default — override in `docs/notes/decisions.md`)

1. **Reachability** — every screen opens; navigation, back, deep links.
2. **CRUD / core flows** — for each entity or flow the module owns.
3. **Lists** — search, filters, sorting, pull-to-refresh, pagination / infinite scroll.
4. **Validation** — required fields, formats, limits, error copy, keyboard types.
5. **Permissions and states** — roles; OS permissions (camera, location, notifications); offline; background/foreground; interruptions.
6. **Edge cases** — selectively, where the risk is real; device matrix tiers in `qa/shared/device-matrix/`.

Per module the chain is: screen recon (mobile MCP / Appium inspector) ↔ checklist alignment →
candidates (prompt 06) → test cases (`prompts/mobile/03`) → screen maps
(`automation/mobile/screens/<screen>_map.py`) → specs (prompt 07) → run → `trace_results.py`.

Defects go to `<NN-module>/bugs/BUG-<CODE>-NNN.md` (template `qa/_templates/bug-mobile.md`) with
evidence in `bugs/evidence/BUG-<CODE>-NNN/`.
