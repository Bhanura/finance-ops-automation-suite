# Synthetic Invoice Processing Dataset

## Overview

This project contains a synthetic Accounts Payable / invoice-processing dataset designed for data analysis, data-quality assessment, SLA monitoring, and finance analytics projects.

No real financial or personally identifiable financial data was used.

All invoice records were programmatically generated using Python and are **synthetic data** created for demonstration and analytical purposes.

## Dataset

The dataset contains approximately 9,000 invoices covering a 12-month period.

The data is divided into five CSV files:

- `invoices_01.csv`
- `invoices_02.csv`
- `invoices_03.csv`
- `invoices_04.csv`
- `invoices_05.csv`

The dataset contains the following fields:

- InvoiceID
- VendorID
- VendorName
- Entity
- Country
- PONumber
- InvoiceDate
- ReceivedDate
- ApprovalDate
- PaymentDate
- Amount
- Currency
- Status
- Processor
- Priority
- ExceptionReason

## Data Quality Issues

The dataset intentionally contains realistic data-quality problems, including:

- Approximately 3% duplicate Invoice IDs
- Missing PO numbers
- Negative invoice amounts
- Approval dates occurring before received dates
- Inconsistent vendor-name spellings
- Mixed date formats
- Some missing processor values
- Invoice exceptions
- Multiple currencies
- Different invoice priorities

These issues are intentionally introduced to support data-cleaning, validation, anomaly detection, and reporting exercises.

## SLA Targets

The `SLA_Targets.xlsx` file contains the target processing times:

| Priority | Approval SLA | Payment SLA |
|---|---:|---:|
| Standard | 5 business days | 30 business days |
| Urgent | 2 business days | 7 business days |

## Disclaimer

This dataset is completely synthetic and does not represent real companies, vendors, invoices, financial transactions, or confidential business information.

It should only be used for educational, portfolio, testing, demonstration, and analytical purposes.