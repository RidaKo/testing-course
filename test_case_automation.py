import re

import pytest
from playwright.sync_api import Page, expect

THRESHOLD = 9
MIN_ITEMS = 2
BASE_URL = "https://demowebshop.com.tricentis.com"

@pytest.mark.parametrize("threshold, min_items", THRESHOLD, MIN_ITEMS)
def registered_user_adds_multiple_items(page: Page):
    page.goto(BASE_URL)
    expect(page).to_have_title(re.compile("Demo Web Shop", re.I))

    page.click(page.get_by_role(link, name="Login"))

    picked_items = []


