from appium.webdriver.webdriver import WebDriver


def swipe_up(driver: WebDriver, duration_ms: int = 600) -> None:
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.8)
    end_y = int(size["height"] * 0.2)
    driver.swipe(start_x, start_y, start_x, end_y, duration_ms)


def swipe_down(driver: WebDriver, duration_ms: int = 600) -> None:
    size = driver.get_window_size()
    start_x = size["width"] // 2
    start_y = int(size["height"] * 0.2)
    end_y = int(size["height"] * 0.8)
    driver.swipe(start_x, start_y, start_x, end_y, duration_ms)


def long_press(driver: WebDriver, element, duration_ms: int = 1500) -> None:
    driver.execute_script(
        "mobile: longClickGesture",
        {
            "elementId": element.id,
            "duration": duration_ms,
        },
    )
