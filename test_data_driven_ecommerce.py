import json
from pathlib import Path

import pytest

from ecommerce_test_helpers import (
    BASE_URL,
    add_candidates_to_cart_from_product_page,
    build_unique_email,
    cart_subtotal,
    collect_price_range_candidates,
    ensure_cart_is_empty,
    logout_if_logged_in,
    proceed_checkout_and_confirm_order,
    read_cart_rows,
    register_new_user,
)

DATA_FILE = Path(__file__).resolve().parent / "test_data" / "ecommerce_scenarios.json"


def _load_scenarios() -> list[dict]:
    with DATA_FILE.open("r", encoding="utf-8") as source:
        return json.load(source)


@pytest.mark.exercise_group_1
@pytest.mark.exercise_4_1
@pytest.mark.parametrize("scenario", _load_scenarios(), ids=lambda s: s["id"])
def test_data_driven_ecommerce_flow_with_pre_and_postconditions(page, scenario: dict) -> None:
    user = scenario["user"]
    address = scenario["billing_address"]
    price_range = scenario["price_range"]
    min_items = scenario["min_items_to_add"]

    email = build_unique_email(user["email_prefix"])
    register_new_user(
        page,
        first_name=user["first_name"],
        last_name=user["last_name"],
        email=email,
        password=user["password"],
    )

    try:
        ensure_cart_is_empty(page)

        candidates = collect_price_range_candidates(
            page,
            min_price_exclusive=price_range["min_exclusive"],
            max_price_exclusive=price_range["max_exclusive"],
        )
        added_items = add_candidates_to_cart_from_product_page(page, candidates)
        assert len(added_items) >= min_items

        page.goto(f"{BASE_URL}cart", wait_until="domcontentloaded")
        rows = read_cart_rows(page)
        expected_subtotal = sum(row.line_total for row in rows)
        assert cart_subtotal(page) == pytest.approx(expected_subtotal, rel=1e-4)

        checkout_summary = proceed_checkout_and_confirm_order(
            page,
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=email,
            address=address,
        )

        assert checkout_summary.subtotal == pytest.approx(expected_subtotal, rel=1e-4)
        assert set(item.name for item in added_items).issubset(
            set(checkout_summary.item_names)
        )
    finally:
        ensure_cart_is_empty(page)
        logout_if_logged_in(page)
