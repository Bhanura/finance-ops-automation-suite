import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker
from openpyxl import Workbook


# ============================================================
# Configuration
# ============================================================

fake = Faker()
random.seed(42)

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

NUM_INVOICES = 9000

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)


# ============================================================
# Reference data
# ============================================================

vendors = [
    ("V001", "ABC Supplies Ltd", "Sri Lanka"),
    ("V002", "Global Tech Solutions", "India"),
    ("V003", "Lanka Office Systems", "Sri Lanka"),
    ("V004", "Prime Logistics", "Singapore"),
    ("V005", "NexGen Software", "United States"),
    ("V006", "Metro Stationery", "Sri Lanka"),
    ("V007", "Asia Pacific Trading", "Malaysia"),
    ("V008", "CloudWorks Inc", "United States"),
    ("V009", "Bright Services", "United Kingdom"),
    ("V010", "Oceanic Imports", "Australia"),
    ("V011", "Smart Solutions", "Sri Lanka"),
    ("V012", "Vertex Consulting", "India"),
    ("V013", "Digital Edge", "Singapore"),
    ("V014", "GreenLine Suppliers", "Sri Lanka"),
    ("V015", "Eastern Logistics", "Bangladesh"),
]

entities = [
    "Head Office",
    "Manufacturing",
    "Retail",
    "Technology",
    "Operations",
]

processors = [
    "Kamal",
    "Nimal",
    "Sahan",
    "Tharushi",
    "Dilshan",
    "Amaya",
]

priorities = ["Standard", "Urgent"]

currencies = ["LKR", "USD", "EUR", "GBP", "SGD", "AUD"]

status_values = [
    "Paid",
    "Approved",
    "Pending Approval",
    "Exception",
    "Rejected",
]


# ============================================================
# Helper functions
# ============================================================

def random_date(start, end):
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def random_business_days(start_date, min_days, max_days):
    days = random.randint(min_days, max_days)
    current = start_date
    while days > 0:
        current += timedelta(days=1)
        # Monday = 0 ... Friday = 4
        if current.weekday() < 5:
            days -= 1
    return current


def format_mixed_date(date_value):
    """
    Randomly use different date formats.
    """

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
    ]

    return date_value.strftime(random.choice(formats))


def generate_po_number():
    return f"PO-{random.randint(100000, 999999)}"


# ============================================================
# Generate clean base dataset
# ============================================================

rows = []

for i in range(NUM_INVOICES):

    vendor_id, vendor_name, country = random.choice(vendors)

    invoice_date = random_date(START_DATE, END_DATE)

    received_date = invoice_date + timedelta(days=random.randint(0, 7))

    priority = random.choices(
        priorities,
        weights=[0.85, 0.15]
    )[0]

    if priority == "Urgent":
        approval_date = random_business_days(
            received_date,
            1,
            2
        )

        payment_date = random_business_days(
            approval_date,
            2,
            7
        )

    else:
        approval_date = random_business_days(
            received_date,
            1,
            5
        )

        payment_date = random_business_days(
            approval_date,
            5,
            30
        )

    amount = round(random.lognormvariate(mu=10, sigma=1.0), 2)

    currency = random.choice(currencies)

    status = random.choice(status_values)

    if status == "Exception":
        exception_reason = random.choice([
            "Missing PO",
            "Duplicate Invoice",
            "Amount Mismatch",
            "Vendor Mismatch",
            "Approval Delay",
        ])
    else:
        exception_reason = ""

    rows.append({
        "InvoiceID": f"INV-{100000 + i}",
        "VendorID": vendor_id,
        "VendorName": vendor_name,
        "Entity": random.choice(entities),
        "Country": country,
        "PONumber": generate_po_number(),
        "InvoiceDate": invoice_date,
        "ReceivedDate": received_date,
        "ApprovalDate": approval_date,
        "PaymentDate": payment_date,
        "Amount": amount,
        "Currency": currency,
        "Status": status,
        "Processor": random.choice(processors),
        "Priority": priority,
        "ExceptionReason": exception_reason,
    })


df = rows


# ============================================================
# Inject missing PO numbers
# ============================================================

missing_po_count = int(len(df) * 0.05)

for idx in random.sample(range(len(df)), missing_po_count):
    df[idx]["PONumber"] = None


# ============================================================
# Inject negative amounts
# ============================================================

negative_count = int(len(df) * 0.01)

for idx in random.sample(range(len(df)), negative_count):
    df[idx]["Amount"] *= -1


# ============================================================
# Inject approval dates BEFORE received dates
# ============================================================

bad_approval_count = int(len(df) * 0.01)

for idx in random.sample(range(len(df)), bad_approval_count):
    received = df[idx]["ReceivedDate"]
    df[idx]["ApprovalDate"] = received - timedelta(days=random.randint(1, 5))


# ============================================================
# Inject inconsistent vendor names
# ============================================================

vendor_variations = {
    "ABC Supplies Ltd": [
        "ABC Supplies Ltd",
        "ABC Supplies LTD",
        "ABC Supplies Limited",
        "A.B.C Supplies Ltd",
    ],

    "Global Tech Solutions": [
        "Global Tech Solutions",
        "Global Tech solution",
        "Global Technologies Solutions",
        "Global Tech Solutions Ltd",
    ],

    "Lanka Office Systems": [
        "Lanka Office Systems",
        "Lanka Office System",
        "Lanka Office Systems Ltd",
        "LANKA OFFICE SYSTEMS",
    ],

    "Prime Logistics": [
        "Prime Logistics",
        "Prime Logistic",
        "Prime Logistics Ltd",
    ],
}

for original_name, variations in vendor_variations.items():

    indices = [
        idx for idx, row in enumerate(df)
        if row["VendorName"] == original_name
    ]

    sample_size = min(
        int(len(indices) * 0.20),
        len(indices)
    )

    if sample_size > 0:

        for idx in random.sample(indices, sample_size):
            df[idx]["VendorName"] = random.choice(variations)


# ============================================================
# Inject duplicate Invoice IDs
# ============================================================

duplicate_count = int(len(df) * 0.03)

duplicate_source_indices = random.sample(range(len(df)), duplicate_count)
duplicate_target_indices = random.sample(range(len(df)), duplicate_count)

for source, target in zip(duplicate_source_indices, duplicate_target_indices):
    df[target]["InvoiceID"] = df[source]["InvoiceID"]


# ============================================================
# Inject additional missing values
# ============================================================

missing_processor_count = int(len(df) * 0.01)

for idx in random.sample(range(len(df)), missing_processor_count):
    df[idx]["Processor"] = None


# ============================================================
# Mixed date formats
# ============================================================

date_columns = [
    "InvoiceDate",
    "ReceivedDate",
    "ApprovalDate",
    "PaymentDate",
]

for row in df:
    for column in date_columns:
        row[column] = format_mixed_date(row[column])


# ============================================================
# Shuffle the dataset
# ============================================================

random.shuffle(df)


# ============================================================
# Split into 5 files
# ============================================================

chunk_size = (len(df) + 4) // 5

for i in range(5):
    chunk = df[i * chunk_size:(i + 1) * chunk_size]
    output_file = OUTPUT_DIR / f"invoices_{i + 1:02d}.csv"

    with output_file.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=chunk[0].keys())
        writer.writeheader()
        writer.writerows(chunk)

    print(f"Created {output_file} ({len(chunk)} records)")


# ============================================================
# Create SLA Targets Excel file
# ============================================================

sla_file = OUTPUT_DIR / "SLA_Targets.xlsx"
workbook = Workbook()
worksheet = workbook.active
worksheet.title = "SLA_Targets"
worksheet.append([
    "Priority",
    "Approval_SLA_Business_Days",
    "Payment_SLA_Business_Days",
])
worksheet.append(["Standard", 5, 30])
worksheet.append(["Urgent", 2, 7])
workbook.save(sla_file)

print(f"Created {sla_file}")


# ============================================================
# Summary
# ============================================================

print("\nDataset generation completed.")

print(f"Total invoices: {len(df)}")

invoice_ids = [row["InvoiceID"] for row in df]
print(
    "Duplicate InvoiceIDs: "
    f"{len(invoice_ids) - len(set(invoice_ids))}"
)
print(
    "Missing PO numbers: "
    f"{sum(row['PONumber'] is None for row in df)}"
)
print(
    "Negative amounts: "
    f"{sum(row['Amount'] < 0 for row in df)}"
)
print(
    "Missing processors: "
    f"{sum(row['Processor'] is None for row in df)}"
)