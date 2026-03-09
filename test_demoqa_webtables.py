import re
import time

import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

BASE_URL = "https://demoqa.com/"


def _pagination_numbers(page: Page) -> tuple[int, int]:
    page_info = (
        page.locator("div.pagination div.col-auto")
        .filter(has_text=re.compile(r"Page \d+ of \d+"))
        .first
        .inner_text()
    )
    match = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", page_info)
    if not match:
        raise AssertionError(f"Unable to parse pagination info: {page_info!r}")
    return int(match.group(1)), int(match.group(2))


def _add_table_record(page: Page, *, index: int, stamp: int) -> None:
    page.get_by_role("button", name="Add").click()
    expect(page.locator("#registration-form-modal")).to_be_visible()

    page.locator("#firstName").fill(f"Clank{index}")
    page.locator("#lastName").fill("Bober")
    page.locator("#userEmail").fill(f"clank_{stamp}_{index}@example.com")
    page.locator("#age").fill(str(20 + index))
    page.locator("#salary").fill(str(1200 + index))
    page.locator("#department").fill("QA")
    page.locator("#submit").click()

    expect(page.locator("#registration-form-modal")).to_have_count(0)


@pytest.mark.exercise_group_1
@pytest.mark.exercise_2_2
def test_web_tables_pagination_returns_to_one_page_after_delete(page: Page) -> None:
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.get_by_role("heading", name="Elements").click()
    page.get_by_text("Web Tables", exact=True).click()
    expect(page).to_have_url(re.compile(r"/webtables"))

    initial_page, initial_total_pages = _pagination_numbers(page)
    assert initial_page == 1
    assert initial_total_pages == 1

    timestamp = int(time.time())
    for i in range(8):
        _add_table_record(page, index=i, stamp=timestamp)

    current_page, total_pages = _pagination_numbers(page)
    assert current_page == 1
    assert total_pages == 2

    next_button = page.get_by_role("button", name="Next")
    expect(next_button).to_be_enabled()
    next_button.click()
    assert _pagination_numbers(page) == (2, 2)

    delete_button = page.locator("table tbody tr:visible span[title='Delete']").first
    expect(delete_button).to_be_visible()
    delete_button.scroll_into_view_if_needed()
    try:
        delete_button.click(timeout=10000)
    except PlaywrightTimeoutError:
        # DemoQA can occasionally place a floating layout block over the icon in CI.
        delete_button.evaluate("node => node.click()")

    assert _pagination_numbers(page) == (1, 1)
    expect(next_button).to_be_disabled()
