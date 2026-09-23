# Аудит коду застосунку — тестопридатність

**Дата:** 2026-09-23 · **Метод:** статичний аналіз вихідників, без збірок і запусків.
**Репозиторій:** `git@gitlab.triare.net:concert-technologies/flutter.git`
(локально `~/Projects/concert-app`, симлінк `app/` у цьому проекті).

> Це **прогноз** за кодом. Жива сесія (крок 3, `qa/shared/recon-2026-09-23-ios.md`)
> **підтвердила** його на Welcome і Login: Appium бачить тексти як `name`/`label`, стан кнопок
> читається. Іконки без підпису ще не перевірені наживо — вони на екранах після логіну.

## 1. Гілка

| Гілка | Версія | Останній коміт | Висновок |
|---|---|---|---|
| **`development`** | **1.1.1+178** | 2026-08-26 | ✅ **ціль**: найсвіжіша, CR-2 влита |
| `fix/end-survey-in-repeatable-instance` | 1.1.0+177 | 2026-08-03 | влита в `development` |
| `feature/survey-section-cards` | — | 2026-07-27 | влита в `development` |
| `feature/new-login-with-email` | — | 2026-04-26 | ❌ **не влита** (6 комітів поза development) |
| `main` | 0.1.0+37 | 2026-02-24 | застарілий |

Тегів у репозиторії немає. Точну прод-збірку підтверджуємо номером версії в установленій
апці (1.1.0+177 чи 1.1.1+178).

## 2. Збірка

| Параметр | Значення |
|---|---|
| Flutter | **3.41.9**, закріплено через **fvm** (`.fvmrc`); Dart `sdk: 3.11.5` |
| На машині | Flutter 3.47.4, **fvm не встановлений** → потрібен для кроку 2 |
| Flavors | `development` · `staging` · `production` |
| Точка входу DEV | `lib/main_development.dart` |
| Android DEV | `com.concerttechnologies.app.dev`, активність `com.concerttechnologies.app.MainActivity` |
| iOS DEV | bundle id `com.concerttechnologies.app.dev`, схема `development` |
| Prod (для довідки) | `com.ctfieldservices.app` |
| API для DEV | `config.env` у репо → `API_BASE_URL_DEV` = `copsfieldservices.devapi.concerttech.com` — **той самий бекенд, де готуємо дані** |
| Firebase | конфіги для всіх flavors у репо (Android + iOS) |
| `--dart-define` | тільки `CLIENT_BUILD` (див. нижче) |

### Рецепт збірки — перевірено на кроці 2 (2026-09-23)

Згенеровані файли (`lib/generated/**`) у git **не зберігаються**. Без генерації збірка падає на
етапі компіляції Dart: `The getter 'LocaleKeys' isn't defined`, `The getter 'AssetIcons' isn't defined`.
Генерація ассетів **не згадана** в `README.md`/`SETUP.md` апки — лише в `tools/README.md`.

```bash
cd ~/Projects/concert-app
git checkout -B development origin/development
fvm install                                   # Flutter 3.41.9 з .fvmrc (один раз)
fvm flutter pub get
./tools/generate_localization.sh              # → lib/generated/l10n/{locale_keys,codegen_loader}.g.dart
./tools/generate_assets.sh                    # → lib/generated/assets.gen.dart (AssetIcons/AssetLogo/AssetImages)
fvm dart run build_runner build --delete-conflicting-outputs   # freezed / json / drift

# iOS-симулятор — з шимом flutterfire у PATH (див. нижче)
PATH="<QA-repo>/automation/mobile/scripts/build_shims:$PATH" \
  fvm flutter build ios --simulator --flavor development -t lib/main_development.dart --dart-define=CLIENT_BUILD=true
ditto build/ios/iphonesimulator/Runner.app <QA-repo>/automation/mobile/builds/ios/Runner.app
# Android
fvm flutter build apk --flavor development -t lib/main_development.dart --dart-define=CLIENT_BUILD=true
```

Побічні ефекти в клоні: `pod install` переписує в `ios/Podfile.lock` рядок `COCOAPODS:` (1.16.2 → 1.17.0),
залежності не змінюються. Після збірки повертаємо: `git checkout -- ios/Podfile.lock`.
**Шим `flutterfire`.** Xcode-проект має build phase, що безумовно виконує
`flutterfire upload-crashlytics-symbols` — завантаження файлів налагодження у Firebase Crashlytics
замовника. Без FlutterFire CLI збірка падає (`flutterfire: command not found`). Ставити CLI означало б
відправляти дані назовні з кожної тестової збірки, тому в PATH підставляється no-op шим
`automation/mobile/scripts/build_shims/flutterfire`: на бінарник апки не впливає, нічого не відправляє.

Результат першої збірки (2026-09-23): `Runner.app`, `com.concerttechnologies.app.dev`, **1.1.1 (178)**,
назва «[DEV] CT Mobile», 224 МБ; метадані — `automation/mobile/builds/ios/BUILD_INFO.txt`.

Під час першого `pod`/SPM-резолву macOS може спитати доступ `xcodebuild` до збереженого логіна github.com —
відповідати **Deny**: усі iOS-залежності публічні (Firebase, Google, CSQLite).

Режим `CLIENT_BUILD=true` — рішення від 2026-09-23 (`docs/notes/decisions.md`).

### Прапорець `CLIENT_BUILD`

```dart
static const bool profile        = !_isClientBuild;   // ніде не використовується
static const bool debugTools     = !_isClientBuild;   // панель налагодження на списку/деталях джоби
static const bool defaultUsPhone = _isClientBuild;    // +1 за замовчуванням у полі телефону
```

`FeatureFlags.profile` у коді **ніде не читається** — Profile видимий завжди, 35 перевірок
модуля 12-profile не під загрозою. Реальна різниця клієнтської збірки: немає debug-панелі і
телефон за замовчуванням +1. **Питання до власника:** збираємо з `CLIENT_BUILD=true`, щоб
поведінка збігалась із тим, що бачить замовник?

## 3. Локатори — головний висновок

| Що шукали | Знайдено | Значення для автоматизації |
|---|---|---|
| `Semantics(identifier: …)` | **0** на 332 файли | ❌ стабільних ідентифікаторів для нативних драйверів **немає** |
| `semanticsLabel:` | 0 | — |
| `ValueKey(…)` | 7, лише в `survey_section_card.dart` (+анімація цифр) | бачить **тільки** integration-драйвер, нативні — ні |
| Локалізація | одна мова, `assets/translations/en.json` | ✅ тексти стабільні, текстові локатори придатні |
| Текстові поля з `labelText`/`hintText` | 19 полів, 30 підписів | ✅ поля знаходяться за підписом |
| Кнопки з текстом (`AppButton` → `Text(label)`) | 21 | ✅ знаходяться за текстом |
| `IconButton` | 24, **з підписом лише 2** | ❌ **22 іконки без підпису** — тестопридатний дефект |
| `GestureDetector`/`InkWell` | 32 | залежить від тексту всередині |

### 22 іконки без підпису

| Екран | Іконки |
|---|---|
| Список джоб | `wifi`, **`calendar` (перемикач список ↔ календар)** |
| Підтвердження check-in / check-out | `close` |
| Фоторедактор (фотозвіт і опитування) | `undo`, `redo`, `check`, `chevron_left` |
| Картка фото, поле фото в опитуванні | `delete`, кастомна |
| Профіль | `edit`, кастомна |
| SMS Terms, PDF-переглядач | `close`, `download` |

Ці елементи зачіпають **48 з 625 перевірок чеклісту (~8%)**: календар 19, undo/redo/markup/crop 9,
закриття 8, видалення фото 6, редагування профілю 4, завантаження PDF 2.

## 4. Екрани в коді

24 сторінки: splash, welcome, sign-up, sms-terms, sign-in, otp-verification, jobs (список +
календар), job-details, attachments, confirm-check-in, confirm-check-out, notes, add-edit-note,
photo-report, add-photo-metadata, photo-editor, survey-fill, survey-add-photo-metadata,
survey-photo-editor, notifications, profile, edit-profile, pdf-viewer. Роутер — `go_router`.
Усі 12 модулів `qa/mobile/` мають відповідні сторінки.

## 5. Що це означає

- **Шлях A (нативні драйвери + `Semantics(identifier:)`) недоступний** — ідентифікаторів немає,
  а змінювати апку розробники не будуть.
- **Робочий шлях — нативні драйвери + текстові локатори.** Прогноз: придатно для ~90% перевірок.
  Тексти стабільні (одна мова), кнопки й поля мають підписи, а джоби ми створюємо самі з
  унікальною назвою — знаходимо їх за текстом надійно.
- **~8% (іконки без підпису)** — вузьке місце. Варіанти: системний «назад» замість хрестика,
  дотик за позицією відносно якірного елемента (крайній захід, з `note=`), або `Blocked` з
  причиною. Кожен випадок — тестопридатний дефект у контракт для розробників.
- Альтернатива для вузького місця — **integration-драйвер** (`FLUTTER_DRIVER=integration`):
  знаходить іконки за типом і `ValueKey`. Але вимагає локально додати `appium_flutter_server` у
  `pubspec` і зібрати debug-збірку — тобто тестувати **змінений** артефакт. Рішення за власником.
- Рекомендація розробникам на майбутнє: `Semantics(identifier:)` у трьох спільних обгортках
  (`AppButton`, `AppTextField`, `IconButton` з `tooltip`) покрила б більшу частину апки однією зміною.
