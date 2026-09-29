# Survey — Android: розбіжності й питання

Android-етап, recon A1 (2026-09-29, емулятор Pixel 7 · Android 16, debug-збірка): чим Android відрізняється від iOS
і від документів. Спільні рішення модуля — у [`../survey-questions.md`](../survey-questions.md); тут лише Android.
Модель оракула та сама: тести стверджують поведінку застосунку, розбіжність — питання, баг — лише зі слова власника.
Докази: `qa/shared/recon-2026-09-29-android.md`, дампи `qa/shared/recon-dumps/android-2026-09-29/`.

Статус: `відкрите` · `прийнято як є` · `баг`

## Розбіжності (D)

| # | Що | iOS | Android | Докази | Статус |
|---|---|---|---|---|---|
| D-SRV-A1 | Заголовки питань | у підписі картки «N. \nTitle» (TD-SRV-001) | заголовки **кількох** питань злиті в один вузол; у короткому опитуванні — навіть у `hint` поля відповіді: «1. Good? 2. Text? Description» | `survey_short.xml`, `survey_mo3_*.xml` | інфо |
| D-SRV-A2 | Поле тексту в картці з одним полем | саме `TextField` (TD-SRV-002) | злитий вузол `EditText`, **Appium не може вписати текст напряму** («Cannot set the element») — працює тап у поле + введення з клавіатури (`mobile: type`) | `survey_short_filled.xml` | інфо |
| D-SRV-A3 | Варіанти відповідей | — | `RadioButton` / `CheckBox` **з підписами** (зручніше, ніж на iOS) | `survey_mo3_1.xml` | інфо |
| D-SRV-A4 | Дата / час | Material-календар; циферблат не в дереві | той самий календар (дні «15, Tuesday, September 15, 2026»); у циферблаті години / хвилини — повзунки в дереві; текстовий режим — поля Hour / Minute | `survey_date_picker.xml`, `survey_time_picker*.xml` | інфо |
| D-SRV-A5 | Поля дати й часу | — | назва поля лише в `hint` («Select date» / «Select time») — UiSelector за підказкою не шукає; на кроці 3 — інший спосіб | `survey_mo3_2.xml` | інфо |

Не пройдено на recon A1 (інших опитувань не створював): «Repeat section», видалення секції з діалогом, «This field is
required» — перевіряться на прогоні модуля 08 (крок 4).
