from pathlib import Path


REPORT_PATH = Path("weekly_report.txt")
DEFAULT_YOUR_PRICE_MULTIPLIER = 1.12


def snapshot_key(item: dict) -> tuple[str, str]:
    return (item["url"], item["title"])


def estimate_your_price(competitor_price: float) -> float:
    return round(competitor_price * DEFAULT_YOUR_PRICE_MULTIPLIER, 2)


def calculate_price_gap(your_price: float, competitor_price: float) -> tuple[float, float]:
    gap_amount = round(your_price - competitor_price, 2)
    gap_percent = round((gap_amount / competitor_price) * 100, 1)
    return gap_amount, gap_percent


def suggest_action(gap_amount: float, gap_percent: float, competitor_in_stock: bool) -> str:
    if not competitor_in_stock:
        return "Hold price. Competitor is out of stock, so you may have pricing power."

    if gap_amount > 0 and gap_percent >= 10:
        return "Review margin and consider matching or narrowing the gap."

    if gap_amount > 0:
        return "Monitor closely. Competitor is cheaper, but the gap is modest."

    if gap_amount < 0:
        return "You are now the cheapest option. Consider holding price or testing a small increase."

    return "Prices are matched. Hold price unless stock or margin changes."


def build_report(changes: list[dict], current_snapshots: list[dict]) -> str:
    current_by_key = {snapshot_key(item): item for item in current_snapshots}
    stockout_count = sum(1 for item in current_snapshots if not bool(item["in_stock"]))
    undercut_count = 0

    for item in current_snapshots:
        your_price = estimate_your_price(item["price"])
        gap_amount, _ = calculate_price_gap(your_price, item["price"])

        if bool(item["in_stock"]) and gap_amount > 0:
            undercut_count += 1

    lines = [
        "Weekly Competitor Price & Stock Report",
        "=" * 39,
        "",
        f"Products checked: {len(current_snapshots)}",
        f"Changes found: {len(changes)}",
        f"Competitor stockouts: {stockout_count}",
        f"Products where competitor is cheaper: {undercut_count}",
        "",
    ]

    if not changes:
        lines.append("No price or stock changes found since the previous run.")
        lines.append("")
        lines.append("Suggested action: Hold pricing and keep monitoring.")
        return "\n".join(lines)

    lines.append("Executive Summary")
    lines.append("-" * 17)

    for change in changes:
        current_item = current_by_key.get(snapshot_key(change))

        if current_item is None:
            continue

        your_price = estimate_your_price(current_item["price"])
        gap_amount, gap_percent = calculate_price_gap(your_price, current_item["price"])

        if change["type"] == "new_product":
            lines.append(f"New competitor product found: {change['title']}")
            continue

        if change["stock_changed"] and not change["new_in_stock"]:
            lines.append(f"{current_item['competitor']} went out of stock: {change['title']}")

        if change["price_change"] < 0:
            lines.append(
                f"{current_item['competitor']} dropped price by "
                f"{abs(change['price_change']):.2f}: {change['title']}"
            )

        if gap_amount > 0 and bool(current_item["in_stock"]):
            lines.append(
                f"{current_item['competitor']} undercut you by "
                f"{gap_amount:.2f} on {change['title']}"
            )

        if gap_amount < 0:
            lines.append(f"You are now the cheapest option on {change['title']}")

    lines.append("")
    lines.append("Detailed Changes")
    lines.append("-" * 16)

    for change in changes:
        current_item = current_by_key.get(snapshot_key(change))

        if change["type"] == "new_product":
            lines.append(f"NEW: {change['title']}")
            lines.append(f"URL: {change['url']}")
            lines.append("")
            continue

        if current_item is None:
            continue

        your_price = estimate_your_price(current_item["price"])
        gap_amount, gap_percent = calculate_price_gap(your_price, current_item["price"])
        action = suggest_action(gap_amount, gap_percent, bool(current_item["in_stock"]))

        lines.append(change["title"])
        lines.append(f"Competitor: {current_item['competitor']}")
        lines.append(f"Your price: {your_price:.2f} {current_item['currency']}")
        lines.append(f"Competitor old price: {change['old_price']:.2f} {current_item['currency']}")
        lines.append(f"Competitor new price: {change['new_price']:.2f} {current_item['currency']}")
        lines.append(f"Competitor price change: {change['price_change']:+.2f}")
        lines.append(f"You are {gap_percent:.1f}% above the lowest competitor.")

        if change["stock_changed"]:
            lines.append(
                f"Competitor stock changed: {change['old_in_stock']} -> {change['new_in_stock']}"
            )

        if gap_amount > 0 and bool(current_item["in_stock"]):
            lines.append(f"Competitor undercut you by {gap_amount:.2f}.")
        elif gap_amount > 0:
            lines.append(
                f"Competitor price is lower by {gap_amount:.2f}, but they are out of stock."
            )
        elif gap_amount < 0:
            lines.append(f"You are cheaper by {abs(gap_amount):.2f}.")
        else:
            lines.append("Your price matches the competitor.")

        lines.append(f"Suggested action: {action}")
        lines.append(f"URL: {change['url']}")
        lines.append("")

    lines.append("Current Tracked Variants")
    lines.append("-" * 24)

    for item in current_snapshots:
        stock_status = "In stock" if bool(item["in_stock"]) else "Out of stock"
        lines.append(
            f"{item['title']} | Competitor price: "
            f"{item['price']:.2f} {item['currency']} | {stock_status}"
        )

    return "\n".join(lines)


def save_report(report_text: str, path: Path = REPORT_PATH) -> None:
    path.write_text(report_text, encoding="utf-8")
