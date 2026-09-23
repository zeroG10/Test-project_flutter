"""Під'єднатись до ВЖЕ відкритої апки (без перезапуску/перевстановлення) і зняти дерево поточного екрана.

Інструмент розвідки для побудови карт екранів (не тест). Потрібні: запущений Appium, симулятор з
відкритою апкою на потрібному екрані. Навігацію між екранами робити вручну або через mobile MCP.

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/dump_screen.py <назва_екрана> ../../qa/shared/recon-dumps/<папка>

Зберігає <назва_екрана>.xml (повний page_source) і друкує значущі елементи: тип, name, enabled, visible, позицію.
"""
import sys, xml.etree.ElementTree as ET
from pathlib import Path
from appium import webdriver
from appium.options.ios import XCUITestOptions
from config.settings import settings
name, out = sys.argv[1], Path(sys.argv[2])
o = XCUITestOptions(); o.device_name = settings.ios_device_name; o.platform_version = settings.ios_platform_version
o.bundle_id = settings.ios_bundle_id; o.no_reset = True; o.auto_accept_alerts = True
o.set_capability("appium:forceAppLaunch", False); o.set_capability("appium:shouldTerminateApp", False)
drv = webdriver.Remote(settings.appium_url, options=o)
try:
    src = drv.page_source; (out / f"{name}.xml").write_text(src)
    rows = []
    for el in ET.fromstring(src).iter():
        t = el.tag.replace("XCUIElementType", ""); a = el.attrib
        if t in ("AppiumAUT", "Application", "Window"): continue
        if t == "Other" and not (a.get("name") or a.get("label")): continue
        if a.get("visible") == "false" and t in ("Other", "ScrollView"): continue
        nm = a.get("name")
        rows.append(f"  {t:<11} name={(repr(nm) if nm else '—'):<42.42} en={a.get('enabled'):<5} vis={a.get('visible'):<5} @{a.get('x')},{a.get('y')} {a.get('width')}x{a.get('height')}")
    print(f"==== {name}: {len(rows)} ===="); print("\n".join(rows))
finally:
    drv.quit()
