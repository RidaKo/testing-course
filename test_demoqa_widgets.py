import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.exercise_group_1
@pytest.mark.exercise_3_1
def test_progress_bar_uses_synchronization_without_sleep(page: Page) -> None:
    page.goto("https://demoqa.com/progress-bar", wait_until="domcontentloaded")

    progress = page.locator("#progressBar .progress-bar")
    expect(progress).to_have_attribute("aria-valuenow", "0")
    expect(page.locator("#resetButton")).to_have_count(0)

    page.locator("#startStopButton").click()
    page.wait_for_function(
        "value => Number(document.querySelector('#progressBar .progress-bar')"
        ".getAttribute('aria-valuenow')) >= value",
        arg=75,
    )
    page.get_by_role("button", name="Stop").click()

    stopped_value = int(progress.get_attribute("aria-valuenow") or "0")
    assert 75 <= stopped_value < 100

    page.get_by_role("button", name="Start").click()
    expect(progress).to_have_attribute("aria-valuenow", "100")
    expect(page.get_by_role("button", name="Reset")).to_be_visible()

    page.get_by_role("button", name="Reset").click()
    expect(progress).to_have_attribute("aria-valuenow", "0")


@pytest.mark.exercise_group_1
@pytest.mark.exercise_3_2
def test_dynamic_properties_change_asynchronously(page: Page) -> None:
    page.goto("https://demoqa.com/dynamic-properties", wait_until="domcontentloaded")

    enable_after = page.locator("#enableAfter")
    color_change = page.locator("#colorChange")
    initial_class = color_change.get_attribute("class") or ""

    assert not enable_after.is_enabled()
    expect(enable_after).to_be_enabled(timeout=12000)

    expect(page.locator("#visibleAfter")).to_be_visible(timeout=12000)

    expect(color_change).to_have_class(re.compile(r".*text-danger.*"), timeout=12000)
    updated_class = color_change.get_attribute("class") or ""
    assert updated_class != initial_class
