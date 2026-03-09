import pytest

from ecommerce_test_helpers import (
    BASE_URL,
    add_candidates_to_cart_from_product_page,
    build_unique_email,
    cart_subtotal,
    collect_price_range_candidates,
    proceed_checkout_and_confirm_order,
    read_cart_rows,
    register_new_user,
    remove_first_cart_item,
    update_first_cart_item_quantity,
)

MIN_PRICE_EXCLUSIVE = 9
MAX_PRICE_EXCLUSIVE = 900
MIN_ITEMS_TO_ADD = 2


@pytest.mark.exercise_group_1
@pytest.mark.exercise_2_1
def test_registered_user_adds_price_range_items_and_completes_checkout(page):
    email = build_unique_email("exercise2")
    password = "P@ssword123"
    address = {
        "country": "United States",
        "state": "AA (Armed Forces Americas)",
        "city": "New York",
        "address_1": "120 Testing Avenue",
        "postal_code": "10001",
        "phone": "5551234567",
    }

    register_new_user(
        page,
        first_name="Clanker",
        last_name="Bro",
        email=email,
        password=password,
    )

    candidates = collect_price_range_candidates(
        page,
        min_price_exclusive=MIN_PRICE_EXCLUSIVE,
        max_price_exclusive=MAX_PRICE_EXCLUSIVE,
    )
    assert len(candidates) >= MIN_ITEMS_TO_ADD

    added_items = add_candidates_to_cart_from_product_page(page, candidates)
    assert len(added_items) >= MIN_ITEMS_TO_ADD

    page.goto(f"{BASE_URL}cart", wait_until="domcontentloaded")
    cart_rows = read_cart_rows(page)
    cart_names = {row.name for row in cart_rows}
    added_names = {item.name for item in added_items}
    assert added_names.issubset(cart_names)

    for row in cart_rows:
        assert MIN_PRICE_EXCLUSIVE < row.unit_price < MAX_PRICE_EXCLUSIVE
        assert row.line_total == pytest.approx(row.unit_price * row.quantity, rel=1e-4)

    expected_initial_subtotal = sum(row.line_total for row in cart_rows)
    assert cart_subtotal(page) == pytest.approx(expected_initial_subtotal, rel=1e-4)

    changed_name = update_first_cart_item_quantity(page, quantity=10)
    updated_rows = read_cart_rows(page)
    changed_row = next(row for row in updated_rows if row.name == changed_name)
    assert changed_row.quantity == 10
    assert changed_row.line_total == pytest.approx(changed_row.unit_price * 10, rel=1e-4)

    subtotal_before_remove = cart_subtotal(page)
    removed_name = remove_first_cart_item(page)
    rows_after_remove = read_cart_rows(page)
    assert removed_name not in {row.name for row in rows_after_remove}

    expected_subtotal_after_remove = sum(row.line_total for row in rows_after_remove)
    actual_subtotal_after_remove = cart_subtotal(page)
    assert actual_subtotal_after_remove == pytest.approx(
        expected_subtotal_after_remove, rel=1e-4
    )
    assert actual_subtotal_after_remove < subtotal_before_remove

    checkout_summary = proceed_checkout_and_confirm_order(
        page,
        first_name="Clanker",
        last_name="Bro",
        email=email,
        address=address,
    )
    remaining_names = {row.name for row in rows_after_remove}
    assert remaining_names.issubset(set(checkout_summary.item_names))
    assert checkout_summary.subtotal == pytest.approx(
        expected_subtotal_after_remove, rel=1e-4
    )

    expected_checkout_total = (
        checkout_summary.subtotal
        + checkout_summary.shipping
        + checkout_summary.payment_fee
        + checkout_summary.tax
    )
    assert checkout_summary.total == pytest.approx(expected_checkout_total, rel=1e-4)
