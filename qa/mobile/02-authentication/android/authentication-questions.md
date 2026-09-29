# Authentication — Android: розбіжності й питання

Android-етап, recon A1 (2026-09-29, емулятор Pixel 7 · Android 16, debug-збірка): чим Android відрізняється від iOS
і від документів. Спільні рішення модуля — у [`../authentication-questions.md`](../authentication-questions.md); тут лише Android.
Модель оракула та сама: тести стверджують поведінку застосунку, розбіжність — питання, баг — лише зі слова власника.
Докази: `qa/shared/recon-2026-09-29-android.md`, дампи `qa/shared/recon-dumps/android-2026-09-29/`.

Статус: `відкрите` · `прийнято як є` · `баг`

## Розбіжності (D)

| # | Що | iOS | Android | Докази | Статус |
|---|---|---|---|---|---|
| D-AUTH-A1 | Запит дозволу на сповіщення | при першому запуску, до Welcome | **після входу** (і на старті, якщо дозволу немає): системний діалог Allow / Don't allow (`com.android.permissioncontroller`) | `perm_notifications.xml` | **прийнято як є** (власник, 2026-09-29) |
| D-AUTH-A2 | Privacy Policy / Terms & Conditions | вбудований браузер SFSafariViewController, Close — лише тап за координатами | **Chrome Custom Tabs**: кнопка `Close tab` (стабільний id), тап працює; адреса `concerttech.com` | `browser_privacy.xml`, `browser_terms.xml` | відкрите |
| D-AUTH-A3 | Тексти й поведінка екранів | — | Welcome, Login, код, реєстрація, SMS Terms — **ті самі тексти й поведінка** (D-1…D-12 діють), включно з пасткою «Incorrect code.» у дереві до вводу | `welcome.xml`, `login.xml`, `otp.xml`, `registration*.xml`, `sms_terms*.xml` | інфо |

## Питання (Q)

| # | Питання | Рекомендація | Статус |
|---|---|---|---|
| Q-AUTH-A1 | Запит на сповіщення після входу: обробляю його у фікстурі входу («Allow», як на iOS), окремим екраном у `screens/android/`. Ок? | так | **закрите** (власник, 2026-09-29: «так») |
