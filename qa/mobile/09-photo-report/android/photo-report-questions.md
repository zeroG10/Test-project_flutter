# Photo report — Android: розбіжності й питання

Android-етап, recon A1 (2026-09-29, емулятор Pixel 7 · Android 16, debug-збірка): чим Android відрізняється від iOS
і від документів. Спільні рішення модуля — у [`../photo-report-questions.md`](../photo-report-questions.md); тут лише Android.
Модель оракула та сама: тести стверджують поведінку застосунку, розбіжність — питання, баг — лише зі слова власника.
Докази: `qa/shared/recon-2026-09-29-android.md`, дампи `qa/shared/recon-dumps/android-2026-09-29/`.

Статус: `відкрите` · `прийнято як є` · `баг`

## Розбіжності (D)

| # | Що | iOS | Android | Докази | Статус |
|---|---|---|---|---|---|
| D-PHR-A1 | Вибір фото | системний PHPicker, клітинок немає в дереві — тап за позицією | **Android Photo Picker** (`com.google.android.photopicker`): клітинки в дереві з підписом «Photo taken on <дата>»; порядок — за датою зйомки | `photo_picker.xml` | інфо |
| D-PHR-A2 | Редактор фото | 4 кнопки без підписів; палітри немає в дереві | Back **з підписом**, «готово» без підпису, Crop / Markup з підписами; у розмітці палітра **є** в дереві (7 елементів без підписів) | `photo_editor*.xml` | інфо |
| D-PHR-A3 | Решта | — | опис, теги, Save, тост «Photo added successfully», сітка «опис\nтег», значок видалення без підпису, діалоги видалення й «Unsaved Changes», «Edit photo» — **як на iOS** | `photo_*.xml` | інфо |
