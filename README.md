# Shopify Competitor Price Monitor

A Python tool that monitors a Shopify product, stores price and stock snapshots, detects changes, and generates a business-style weekly report that can be sent by email.

## What It Does

- Scrapes a real Shopify product JSON endpoint
- Saves historical price and stock snapshots in SQLite
- Compares the latest scrape against the previous run
- Generates a competitor price and stock report
- Sends the report by email through SMTP
- Includes a GitHub Actions workflow for scheduled runs

## Demo Target

The default demo target used during development is:

```text
https://www.deathwishcoffee.com/products/death-wish-coffee
```

## Local Setup

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set Shopify variables in PowerShell:

```powershell
$env:SHOPIFY_STORE_URL="https://www.deathwishcoffee.com"
$env:SHOPIFY_PRODUCT_HANDLE="death-wish-coffee"
$env:COMPETITOR_NAME="Death Wish Coffee"
```

Set email variables in PowerShell:

```powershell
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="your_email@gmail.com"
$env:SMTP_PASSWORD="your_app_password"
$env:REPORT_FROM="your_email@gmail.com"
$env:REPORT_TO="your_email@gmail.com"
```

Run the monitor:

```bash
python main.py --source shopify
```

Run the monitor and send the report by email:

```bash
python main.py --source shopify --send-email
```

## GitHub Actions Secrets

Add these repository secrets in GitHub:

```text
SHOPIFY_STORE_URL
SHOPIFY_PRODUCT_HANDLE
COMPETITOR_NAME
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
REPORT_FROM
REPORT_TO
```

Go to:

```text
Repository -> Settings -> Secrets and variables -> Actions -> New repository secret
```

## Security Notes

Do not commit real passwords, API keys, or `.env` files.

This repo includes `.gitignore` entries for:

```text
.env
.env.*
price_monitor.db
weekly_report.txt
__pycache__/
```

## Portfolio Summary

This project demonstrates an automated ecommerce monitoring workflow:

```text
Shopify product -> snapshot storage -> change detection -> business report -> email delivery -> scheduled automation
```
