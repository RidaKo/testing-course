import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page, expect

BASE_URL = "https://demowebshop.tricentis.com/"


@dataclass
class ProductCandidate:
    name: str
    price: float
    url: str


@dataclass
class CartRow:
    name: str
    unit_price: float
    quantity: int
    line_total: float


@dataclass
class CheckoutSummary:
    item_names: list[str]
    subtotal: float
    shipping: float
    payment_fee: float
    tax: float
    total: float


def parse_money(raw_value: str) -> float:
    numeric = re.sub(r"[^0-9.\-]", "", raw_value)
    return float(numeric) if numeric else 0.0


def build_unique_email(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}@example.com"


def register_new_user(
    page: Page,
    *,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    expect(page).to_have_title(re.compile("Demo Web Shop", re.I))

    page.get_by_role("link", name="Register", exact=True).click()
    page.locator("#gender-male").check()
    page.locator("#FirstName").fill(first_name)
    page.locator("#LastName").fill(last_name)
    page.locator("#Email").fill(email)
    page.locator("#Password").fill(password)
    page.locator("#ConfirmPassword").fill(password)
    page.locator("#register-button").click()

    expect(page.locator(".result")).to_contain_text("Your registration completed")
    expect(page.get_by_role("link", name=email)).to_be_visible()


def ensure_cart_is_empty(page: Page) -> None:
    page.goto(urljoin(BASE_URL, "cart"), wait_until="domcontentloaded")
    remove_checkboxes = page.locator("input[name='removefromcart']")
    if remove_checkboxes.count() > 0:
        for index in range(remove_checkboxes.count()):
            remove_checkboxes.nth(index).check()
        page.locator("input[name='updatecart']").click()
    expect(page.locator("input[name='removefromcart']")).to_have_count(0)


def logout_if_logged_in(page: Page) -> None:
    logout_link = page.get_by_role("link", name="Log out", exact=True)
    if logout_link.count() > 0:
        logout_link.click()


def _collect_products_from_current_listing(
    page: Page,
    *,
    min_price_exclusive: float,
    max_price_exclusive: float,
) -> list[ProductCandidate]:
    products: list[ProductCandidate] = []
    cards = page.locator(".product-item")
    for index in range(cards.count()):
        card = cards.nth(index)
        name = card.locator("h2.product-title a").inner_text().strip()
        price_text = card.locator(".prices .actual-price").first.inner_text().strip()
        price = parse_money(price_text)
        if not (min_price_exclusive < price < max_price_exclusive):
            continue

        href = card.locator("h2.product-title a").get_attribute("href")
        if not href:
            continue
        products.append(
            ProductCandidate(name=name, price=price, url=urljoin(BASE_URL, href))
        )
    return products


def collect_price_range_candidates(
    page: Page,
    *,
    min_price_exclusive: float,
    max_price_exclusive: float,
) -> list[ProductCandidate]:
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.locator("ul.top-menu a[href='/books']").click()
    books = _collect_products_from_current_listing(
        page,
        min_price_exclusive=min_price_exclusive,
        max_price_exclusive=max_price_exclusive,
    )

    page.locator("ul.top-menu a[href='/computers']").click()
    page.locator("a[href='/desktops']").first.click()
    desktops = _collect_products_from_current_listing(
        page,
        min_price_exclusive=min_price_exclusive,
        max_price_exclusive=max_price_exclusive,
    )

    deduped: dict[str, ProductCandidate] = {}
    for item in books + desktops:
        deduped.setdefault(item.name, item)
    return list(deduped.values())


def _close_bar_notification_if_open(page: Page) -> None:
    close_button = page.locator("#bar-notification span.close")
    if close_button.count() > 0 and close_button.is_visible():
        close_button.click()


def add_candidates_to_cart_from_product_page(
    page: Page, candidates: list[ProductCandidate]
) -> list[ProductCandidate]:
    added: list[ProductCandidate] = []
    for candidate in candidates:
        page.goto(candidate.url, wait_until="domcontentloaded")
        add_button = page.locator("div.add-to-cart input[value='Add to cart']")
        if add_button.count() == 0:
            continue

        add_button.first.click()
        bar = page.locator("#bar-notification")
        expect(bar).to_be_visible()
        message = bar.inner_text().lower()
        if "added to your shopping cart" in message:
            added.append(candidate)
        _close_bar_notification_if_open(page)
    return added


def read_cart_rows(page: Page) -> list[CartRow]:
    rows: list[CartRow] = []
    row_locator = page.locator("tr.cart-item-row")
    for index in range(row_locator.count()):
        row = row_locator.nth(index)
        name = row.locator("td.product a.product-name").inner_text().strip()
        unit_price = parse_money(
            row.locator("td.unit-price span.product-unit-price").inner_text()
        )
        quantity = int(row.locator("td.qty input.qty-input").input_value())
        line_total = parse_money(
            row.locator("td.subtotal span.product-subtotal").inner_text()
        )
        rows.append(
            CartRow(
                name=name,
                unit_price=unit_price,
                quantity=quantity,
                line_total=line_total,
            )
        )
    return rows


def cart_subtotal(page: Page) -> float:
    table_rows = page.locator(".cart-footer .cart-total tr")
    for index in range(table_rows.count()):
        row = table_rows.nth(index)
        left_text = row.locator("td.cart-total-left").inner_text().strip().lower()
        if "sub-total" in left_text:
            right_text = row.locator("td.cart-total-right").inner_text()
            return parse_money(right_text)
    raise AssertionError("Unable to locate cart subtotal row.")


def update_first_cart_item_quantity(page: Page, quantity: int) -> str:
    first_row = page.locator("tr.cart-item-row").first
    changed_item_name = first_row.locator("td.product a.product-name").inner_text().strip()
    first_row.locator("td.qty input.qty-input").fill(str(quantity))
    page.locator("input[name='updatecart']").click()
    expect(
        page.locator("tr.cart-item-row td.qty input.qty-input").first
    ).to_have_value(str(quantity))
    return changed_item_name


def remove_first_cart_item(page: Page) -> str:
    first_row = page.locator("tr.cart-item-row").first
    removed_name = first_row.locator("td.product a.product-name").inner_text().strip()
    first_row.locator("input[name='removefromcart']").check()
    page.locator("input[name='updatecart']").click()
    expect(
        page.locator("tr.cart-item-row td.product a.product-name").filter(
            has_text=removed_name
        )
    ).to_have_count(0)
    return removed_name


def _select_state_for_country(page: Page, desired_state: str | None) -> None:
    page.wait_for_function(
        "() => document.querySelectorAll('#BillingNewAddress_StateProvinceId option').length > 0"
    )
    options_locator = page.locator("#BillingNewAddress_StateProvinceId option")
    labels = options_locator.all_inner_texts()

    if desired_state and desired_state in labels:
        page.locator("#BillingNewAddress_StateProvinceId").select_option(
            label=desired_state
        )
        return

    fallback_value = options_locator.first.get_attribute("value")
    if fallback_value is None:
        raise AssertionError("State/province dropdown has no options.")
    page.locator("#BillingNewAddress_StateProvinceId").select_option(value=fallback_value)


def _fill_billing_address_if_visible(
    page: Page,
    *,
    first_name: str,
    last_name: str,
    email: str,
    address: dict[str, str],
) -> None:
    address_select = page.locator("#billing-address-select")
    if address_select.count() > 0 and address_select.is_visible():
        available = address_select.locator("option").all_inner_texts()
        if "New Address" in available:
            address_select.select_option(label="New Address")

    billing_first_name = page.locator("#BillingNewAddress_FirstName")
    if billing_first_name.count() == 0 or not billing_first_name.is_visible():
        return

    billing_first_name.fill(first_name)
    page.locator("#BillingNewAddress_LastName").fill(last_name)
    page.locator("#BillingNewAddress_Email").fill(email)
    page.locator("#BillingNewAddress_CountryId").select_option(
        label=address["country"]
    )
    _select_state_for_country(page, address.get("state"))
    page.locator("#BillingNewAddress_City").fill(address["city"])
    page.locator("#BillingNewAddress_Address1").fill(address["address_1"])
    page.locator("#BillingNewAddress_ZipPostalCode").fill(address["postal_code"])
    page.locator("#BillingNewAddress_PhoneNumber").fill(address["phone"])


def _read_checkout_totals(rows: Locator) -> dict[str, float]:
    totals: dict[str, float] = {}
    for index in range(rows.count()):
        row = rows.nth(index)
        label = re.sub(
            r"\s+", " ", row.locator("td").first.inner_text().strip().lower()
        ).rstrip(":")
        value_text = row.locator("td").nth(1).inner_text()
        value = parse_money(value_text)

        if label.startswith("sub-total"):
            totals["sub_total"] = value
        elif label.startswith("shipping"):
            totals["shipping"] = value
        elif "additional fee" in label:
            totals["payment_fee"] = value
        elif label.startswith("tax"):
            totals["tax"] = value
        elif label.startswith("total"):
            totals["total"] = value
    return totals


def _wait_for_actionable_checkout_button(page: Page) -> None:
    page.wait_for_function(
        """
        () => {
          const root = document.querySelector('#checkout-steps');
          if (!root) return false;
          const buttons = Array.from(root.querySelectorAll('input.button-1'));
          return buttons.some((button) => {
            if ((button.value || '').trim().toLowerCase() === 'back') return false;
            const style = window.getComputedStyle(button);
            return style.display !== 'none'
              && style.visibility !== 'hidden'
              && !button.disabled
              && button.offsetParent !== null;
          });
        }
        """
    )


def proceed_checkout_and_confirm_order(
    page: Page,
    *,
    first_name: str,
    last_name: str,
    email: str,
    address: dict[str, str],
) -> CheckoutSummary:
    page.locator("#termsofservice").check()
    page.locator("#checkout").click()
    expect(page).to_have_url(re.compile("onepagecheckout"))
    expect(page.locator("#checkout-steps")).to_be_visible(timeout=20000)

    for _ in range(20):
        _wait_for_actionable_checkout_button(page)
        _fill_billing_address_if_visible(
            page,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
        )

        pickup_checkbox = page.locator("#PickUpInStore")
        if (
            pickup_checkbox.count() > 0
            and pickup_checkbox.is_visible()
            and not pickup_checkbox.is_checked()
        ):
            pickup_checkbox.check()

        confirm_button = page.locator(
            "#confirm-order-buttons-container input.button-1:visible"
        )
        if confirm_button.count() > 0:
            break

        next_buttons = page.locator(
            "#checkout-steps input.button-1:visible:not([value='Back']):not([disabled])"
        )
        expect(next_buttons.first).to_be_visible()
        next_buttons.first.click()

    confirm_button = page.locator(
        "#confirm-order-buttons-container input.button-1:visible"
    )
    expect(confirm_button).to_have_count(1)

    checkout_item_names = page.locator(
        ".order-summary-content tr.cart-item-row td.product a"
    ).all_inner_texts()
    totals = _read_checkout_totals(page.locator(".order-summary-content .cart-total tr"))

    confirm_button.click()
    expect(page).to_have_url(re.compile(r"checkout/completed/?"))
    expect(page.locator(".page-title")).to_contain_text("Thank you")
    expect(page.locator(".section.order-completed")).to_contain_text(
        "successfully processed"
    )

    return CheckoutSummary(
        item_names=checkout_item_names,
        subtotal=totals.get("sub_total", 0.0),
        shipping=totals.get("shipping", 0.0),
        payment_fee=totals.get("payment_fee", 0.0),
        tax=totals.get("tax", 0.0),
        total=totals.get("total", 0.0),
    )
