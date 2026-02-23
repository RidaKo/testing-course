import re
from playwright.sync_api import Page, expect

def test_homepage_opens(page: Page):
    page.goto("https://demowebshop.tricentis.com/")
    expect(page).to_have_title(re.compile("Demo Web Shop"))
    expect(page.get_by_role("link", name="Tricentis Demo Web Shop")).to_be_visible()
    expect(page.get_by_role("link", name="Register")).to_be_visible()
    expect(page.get_by_role("link", name="Log in")).to_be_visible()
