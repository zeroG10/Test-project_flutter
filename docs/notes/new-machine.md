# Розгортання проєкту на іншому Mac

Що потрібно, щоб на новому комп'ютері стягнути цей проєкт і ганяти мобільні тести, звіти та скіли.
Git містить увесь код, документи, скіли й фінальні звіти; **секретів, збірок застосунку й сирих результатів
прогонів у git немає** — їх переносять окремо (розділ 2).

## 1. Стягнути

```bash
git clone https://github.com/zeroG10/Test-project_flutter.git
cd Test-project_flutter        # гілка main — увесь робочий проєкт (main = qa/android з 2026-10-06)
```

## 2. Що перенести вручну (не в git)

Передавати захищеним каналом — не відкритим листом чи повідомленням.

| Що | Куди покласти | Розмір | Без нього |
|---|---|---|---|
| `automation/mobile/.env` — тестові акаунти (обидва), коди, доступ до API для тестових даних, порти Appium | `automation/mobile/.env` | 3 КБ | усі тести `Blocked` |
| Збірка Android: `app-development-debug.apk` + `BUILD_INFO.txt` | `automation/mobile/builds/android/` | 186 МБ | Android `Blocked: build not found` |
| Збірка iOS: `Runner.app` (тека цілком) + `BUILD_INFO.txt` | `automation/mobile/builds/ios/` | 224 МБ | iOS `Blocked: build not found` |
| Фінальні прогони: `results/ios/{final-1,final-2,stable-1,stable-2,stable-3}`, `results/android/2026-10-02-final-u{1,2,3}` | `automation/mobile/results/…` (ті самі шляхи) | 414 МБ | тести йдуть; не перезбираються звіти й немає бази для порівняння прогонів |

Збірки можна не переносити, а зібрати заново з репозиторію застосунку (лише читання; команда й версії — у
`BUILD_INFO.txt`, для iOS — заглушка `automation/mobile/scripts/build_shims/`; деталі — `automation/mobile/builds/README.md`).

## 3. Інструменти на Mac

- Xcode + симулятор **iPhone 17, iOS 26.5**.
- Android SDK + емулятор **`Pixel_7_API_36`** (Pixel 7, Android 16, Google APIs arm64, 4 ГБ).
- Appium 3.4.x з драйверами `uiautomator2` і `xcuitest`; `uv`; Node.js; `allure` (за бажанням).
- Перевірка всього разом: `bash automation/mobile/scripts/doctor.sh` — виправити кожен пункт `MISSING`.

```bash
cd automation/mobile && uv sync
cd ../tools && uv sync
```

## 4. Перевірити без пристрою (≈1 хв)

```bash
cd automation/mobile
uv run python -m unittest discover -s unit_tests              # самотест харнесу
uv run pytest --platform=android --collect-only -q | tail -1  # 149 тестів
scripts/qa.sh both all --dry-run                              # план: обидві платформи, два акаунти, два порти
cd ../tools && uv run pytest -q                               # самотест інструментів звітів
```

## 5. Перший прогін

У Claude Code: `/qa-mobile-run android splash` — або руками `cd automation/mobile && scripts/qa.sh android splash`.
Як працюють команди й скіли: [mobile-qa-skills.md](mobile-qa-skills.md) (англійською —
[mobile-qa-skills.en.md](mobile-qa-skills.en.md)). Паралельні прогони й ліміт входів на DEV:
[automation/mobile/PARALLEL-RUNS.md](../../automation/mobile/PARALLEL-RUNS.md).

## 6. Контекст для Claude на новому комп'ютері

Пам'ять Claude з цього Mac (`~/.claude/projects/…`) у git не потрапляє. Усе потрібне записано в репозиторії:
`CLAUDE.md` (правила), `docs/notes/session-handoff.md` (стан роботи, починати з розділів 3э, 3ь, 3ъ),
`docs/notes/decisions.md` (рішення власника), `docs/notes/android-plan.md` (план етапу Android). Першим
повідомленням у новій сесії: «прочитай handoff і продовжуй».
