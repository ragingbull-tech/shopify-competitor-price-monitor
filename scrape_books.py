from scraper import scrape_page


def main() -> None:
    snapshots = scrape_page()

    for item in snapshots:
        print(
            f"{item['title']} | GBP {item['price']} | "
            f"in_stock={item['in_stock']} | rating={item['rating']}"
        )


if __name__ == "__main__":
    main()
