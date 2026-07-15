from diff import compare_snapshots
from report import build_report, save_report
from storage import (
    connect,
    create_scrape_run,
    get_latest_run_ids,
    get_snapshots_for_run,
    initialize_database,
    save_snapshots,
)


def simulate_changes() -> int:
    connection = connect()
    initialize_database(connection)
    latest_run_ids = get_latest_run_ids(connection, limit=1)

    if not latest_run_ids:
        raise RuntimeError("Run main.py once before simulating changes.")

    latest_snapshots = get_snapshots_for_run(connection, latest_run_ids[0])
    simulated = []

    for index, snapshot in enumerate(latest_snapshots):
        item = dict(snapshot)

        if index == 0:
            item["price"] = round(item["price"] - 5, 2)

        if index == 1:
            item["price"] = round(item["price"] + 3, 2)

        if index == 2:
            item["in_stock"] = 0 if item["in_stock"] else 1
            item["stock_text"] = "Simulated stock change"

        simulated.append(item)

    run_id = create_scrape_run(connection, simulated[0]["observed_at"])
    save_snapshots(connection, run_id, simulated)

    previous_snapshots = get_snapshots_for_run(connection, latest_run_ids[0])
    current_snapshots = get_snapshots_for_run(connection, run_id)
    changes = compare_snapshots(previous_snapshots, current_snapshots)
    report_text = build_report(changes, current_snapshots)
    save_report(report_text)

    connection.close()
    return run_id


if __name__ == "__main__":
    new_run_id = simulate_changes()
    print(f"Created simulated run {new_run_id}")
