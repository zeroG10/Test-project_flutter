# builds/ — app artefacts under test (gitignored)

Nothing in here is committed. Drop the build for the platform you run, point `.env` at it,
and `conftest.py` refuses to start a session (reports `Blocked: build not found`) when the
file is absent — a missing build is never a silent skip.

| Folder | What goes here | `.env` key | Produced by |
|---|---|---|---|
| `android/` | `.apk` for the emulator or a USB device (debug or release) | `ANDROID_APP_PATH=./builds/android/app-debug.apk` | Gradle `assembleDebug` / `assembleRelease`, or `flutter build apk` |
| `ios/` | `.app` bundle for the **simulator** (a directory — copy it whole) | `IOS_APP_PATH=./builds/ios/App.app` | Xcode "Build" for *Any iOS Simulator Device*, or `flutter build ios --simulator` (`build/ios/iphonesimulator/Runner.app`) |
| `ios/` | `.ipa` for a **real device** (needs a dev-signed build + WebDriverAgent signing) | `IOS_APP_PATH=./builds/ios/App.ipa` | Xcode archive / `flutter build ipa` |
| `flutter/` | Flutter **integration-driver** builds only: debug/profile builds that compile in the `appium_flutter_server` package (`FLUTTER_DRIVER=integration`) | `ANDROID_APP_PATH=./builds/flutter/app-debug.apk` or `IOS_APP_PATH=./builds/flutter/Runner.app` | `flutter build apk --debug` / `flutter build ios --simulator --debug` with the server dependency added |

## Flutter apps — build per platform

Flutter is an app kind, not a platform. Build once per OS and drop the result in that OS's
folder; the default native drivers test the release build through `Semantics(identifier:)`:

```bash
cd <flutter-app>
flutter build apk --release                 # → build/app/outputs/flutter-apk/app-release.apk  → builds/android/
flutter build ios --simulator --no-codesign # → build/ios/iphonesimulator/Runner.app           → builds/ios/
```

Only when the integration driver is opted in (`APP_KIND=flutter` + `FLUTTER_DRIVER=integration`)
do you need a debug build with the server package — keep those in `flutter/` so a release
build and a debug build never get confused.

## Rules

- A build is an input, not a test artefact: record its version/commit in the run report.
- Emulator/simulator builds ≠ device builds (architecture and signing differ). Name them.
- Never edit the app under test to make a test pass (QA Doctrine rule 4).
