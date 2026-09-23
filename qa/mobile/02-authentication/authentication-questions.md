# Authentication — питання

Розбіжності між документами і застосунком. За моделлю оракула (`docs/notes/decisions.md`,
2026-09-23) тести стверджують **поведінку застосунку**; тут фіксуємо, щоб розбіжність не загубилась.
Власник може перевести будь-який рядок у баг.

Статус: `відкрите` · `прийнято як є` · `баг`

> **2026-09-23, власник:** усі D-1…D-11 — застосунок поводиться правильно. Тести стверджують поведінку апки; SRS у цих місцях застарілий.

| # | Екран | Документ каже | Застосунок робить | Джерело | Статус |
|---|---|---|---|---|---|
| D-1 | Welcome | заголовок «Welcome to the Concert Technologies» (SRS §3.1.1.1, чекліст) | «Welcome to Concert Technologies' Field Force» | коміт 2026-08-04 «update welcome title for clarity»; recon 2026-09-23 | прийнято як є (власник, 2026-09-23) |
| D-2 | Login | поле «Phone number», вхід лише за телефоном (SRS §3.1.1.4, FR-LOG-01…05) | поле «Phone number / Email», вхід за телефоном або email | recon 2026-09-23; чекліст містить перевірки входу через email | прийнято як є (власник, 2026-09-23) |
| D-3 | Login | кнопка «Log in» (SRS §3.1.1.4) | кнопка «Continue» | recon 2026-09-23 | прийнято як є (власник, 2026-09-23) |
| D-4 | Login | підзаголовок «…Let's get you log in.» | «…Let's get you logged in.» | recon 2026-09-23 | прийнято як є (власник, 2026-09-23) |
| D-5 | OTP | код відправляється натисканням Verify (SRS FR-OTP-05) | код підтверджується автоматично після 4-ї цифри | recon 3b 2026-09-23 | прийнято як є (власник, 2026-09-23) |
| D-6 | Registration | Email **необов'язковий** (SRS §3.1.1.2, FR-REG-04) | чекліст CHK-AUTH-043: Email **обов'язковий** (чекліст писали по живій апці) | чекліст vs SRS; підтвердити на апці в TC-AUTH-011 | прийнято як є (власник, 2026-09-23) |
| D-7 | Registration | зайнятий телефон: «This phone number is already associated with an account.» (FR-REG-11) | чекліст CHK-AUTH-069: «An account with this phone number already exists. Please log in to continue.» | чекліст vs SRS; підтвердити на апці в TC-AUTH-014 | прийнято як є (власник, 2026-09-23) |
| D-8 | Login | невалідний ввід: «Field is required.» (FR-LOG-03); незареєстрований: «No account found with this phone number.» (FR-LOG-08) | чекліст CHK-AUTH-112/122/123: «Format is incorrect.»; «This phone number / email is not registered yet. Create an account to get started.» | чекліст vs SRS; підтвердити на апці в TC-AUTH-007 | прийнято як є (власник, 2026-09-23) |
| D-9 | Registration / SMS Terms | чекліст CHK-AUTH-053: екран SMS Terms відкриває **чекбокс згоди**; CHK-AUTH-056: Accept ставить позначку в **чекбоксі** | SMS Terms відкриває **вибір каналу SMS**; Accept **обирає канал SMS**; чекбокс згоди — окремий крок, лише ставить позначку | recon 3c 2026-09-23 | прийнято як є (власник, 2026-09-23) |
| D-10 | Registration | телефон: «Invalid phone number.» (FR-REG-05) | «Enter a valid phone number» | recon 3c 2026-09-23 | прийнято як є (власник, 2026-09-23) |
| D-11 | Registration | email: «Invalid email address.» (FR-REG-05) | «Email format is incorrect.» | recon 3c 2026-09-23 | прийнято як є (власник, 2026-09-23) |
| D-12 | Login | чекліст CHK-AUTH-112: невалідний формат email / телефону показує «Format is incorrect.» (так само SRS FR-LOG-03 — «Field is required.») | **жодного повідомлення** для `abc@`, `12ab`, `abc`, `abc@x`, `+1abc` — ні під час введення, ні після втрати фокусу; лише неактивна Continue і постійна підказка «Format: +1234567890 or name@example.com» | recon 3d 2026-09-23 (дампи `recon3d_login_format*.xml`, відео) | прийнято як є (власник, 2026-09-23): TC-AUTH-007 стверджує неактивну Continue; CHK-AUTH-112 — Skipped з причиною D-12; рядка «Format is incorrect.» немає в усій історії коду апки — не регресія |
| D-13 | Login | формат email (загальноприйнятий: без пробілів) | `a b@c.com` (пробіл усередині) вважається валідним — Continue стає активною; що відповість сервер, не перевіряли (запит не надсилали) | recon 3d 2026-09-23 | прийнято як є / Skipped (власник, 2026-09-23): пробіли обрізаються перед відправкою — тест не пишемо |

