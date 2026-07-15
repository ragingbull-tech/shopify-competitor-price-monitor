import argparse
import os

from diff import compare_snapshots
from emailer import send_email_report
from report import build_report, save_report
from scraper import scrape_page
from shopify_scraper import scrape_shopify_product
from storage import (
    connect,
    create_scrape_run,
    get_latest_run_ids,
    get_snapshots_for_run,
    initialize_database,
    save_snapshots,
)


def get_snapshots(source: str) -> list[dict]:
    if source == "books":
        return scrape_page()

    if source == "shopify":
        store_url = os.environ["SHOPIFY_STORE_URL"]
        product_handle = os.environ["SHOPIFY_PRODUCT_HANDLE"]
        competitor_name = os.environ.get("COMPETITOR_NAME", "Shopify Competitor")
        return scrape_shopify_product(store_url, product_handle, competitor_name)

    raise ValueError(f"Unknown source: {source}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["books", "shopify"], default="books")
    parser.add_argument("--send-email", action="store_true")
    args = parser.parse_args()

    connection = connect()
    initialize_database(connection)

    snapshots = get_snapshots(args.source)

    if not snapshots:
        raise RuntimeError("No snapshots were collected.")

    run_id = create_scrape_run(connection, snapshots[0]["observed_at"])
    save_snapshots(connection, run_id, snapshots)

    latest_run_ids = get_latest_run_ids(connection, limit=2)
    current_snapshots = get_snapshots_for_run(connection, latest_run_ids[0])

    if len(latest_run_ids) < 2:
        changes = []
    else:
        previous_snapshots = get_snapshots_for_run(connection, latest_run_ids[1])
        changes = compare_snapshots(previous_snapshots, current_snapshots)

    report_text = build_report(changes, current_snapshots)
    save_report(report_text)

    print(f"Saved {len(snapshots)} snapshots in scrape run {run_id}.")
    print(f"Found {len(changes)} changes.")
    print("Wrote weekly_report.txt.")

    if args.send_email:
        subject = f"Competitor report: {len(changes)} changes found"
        email_sent = send_email_report(subject, report_text)

        if not email_sent:
            print("Report was created, but email delivery failed.")

    connection.close()


if __name__ == "__main__":
    main()
