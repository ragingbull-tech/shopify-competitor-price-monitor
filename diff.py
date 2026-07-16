def snapshot_key(item: dict) -> tuple[str, str]:
    return (item["url"], item["title"])


def compare_snapshots(previous: list[dict], current: list[dict]) -> list[dict]:
    previous_by_key = {snapshot_key(item): item for item in previous}
    changes = []

    for current_item in current:
        previous_item = previous_by_key.get(snapshot_key(current_item))

        if previous_item is None:
            changes.append(
                {
                    "type": "new_product",
                    "title": current_item["title"],
                    "url": current_item["url"],
                    "message": "New product found",
                }
            )
            continue

        price_change = round(current_item["price"] - previous_item["price"], 2)
        stock_changed = bool(current_item["in_stock"]) != bool(previous_item["in_stock"])

        if price_change != 0 or stock_changed:
            changes.append(
                {
                    "type": "changed_product",
                    "title": current_item["title"],
                    "url": current_item["url"],
                    "old_price": previous_item["price"],
                    "new_price": current_item["price"],
                    "price_change": price_change,
                    "old_in_stock": bool(previous_item["in_stock"]),
                    "new_in_stock": bool(current_item["in_stock"]),
                    "stock_changed": stock_changed,
                }
            )

    return changes
