import random
from datetime import datetime, timedelta
from app.supabase_client import supabase


# =========================
# BUSINESS UNITS
# =========================
def generate_business_units(num_units=3):
    units = []
    countries = ["Portugal", "Spain", "Germany", "France", "Netherlands"]
    cities = ["Lisbon", "Madrid", "Berlin", "Paris", "Amsterdam"]

    for i in range(num_units):
        units.append({
            "name": f"Business Unit {i+1}",
            "country": random.choice(countries),
            "city": random.choice(cities)
        })
    return units


# =========================
# ASSETS
# =========================
def generate_assets(num_assets=50, unit_id=1):
    asset_types = ["Software", "Machine", "Vehicle", "License", "Infrastructure"]
    statuses = ["Active", "Maintenance", "Inactive"]

    assets = []
    base_code = int(datetime.now().timestamp())

    for i in range(num_assets):
        assets.append({
            "asset_code": f"A-{unit_id}-{base_code+i}",
            "asset_type": random.choice(asset_types),
            "status": random.choice(statuses),
            "business_unit_id": unit_id
        })
    return assets


# =========================
# VENDORS
# =========================
def generate_vendors(num_vendors=5):
    vendor_names = [
        "SAP", "AWS", "Azure", "Siemens", "Bosch",
        "IBM", "Oracle", "Salesforce"
    ]

    vendors = []
    for i in range(num_vendors):
        vendors.append({
            "vendor_name": vendor_names[i % len(vendor_names)],
            "category": random.choice(["Cloud", "Hardware", "Software", "Consulting"])
        })
    return vendors


# =========================
# PROCESSES
# =========================
def generate_processes(num_processes=4):
    process_names = [
        "Data Processing",
        "Maintenance Cycle",
        "System Deployment",
        "Quality Audit"
    ]

    processes = []
    for i in range(num_processes):
        processes.append({
            "process_name": process_names[i % len(process_names)],
            "expected_duration_days": random.randint(1, 14),
            "average_cost": round(random.uniform(500, 5000), 2)
        })
    return processes


# =========================
# OPERATIONS (KPIs LIVE HERE)
# =========================
def generate_operations(
    num_operations=200,
    asset_ids=None,
    vendor_ids=None,
    process_ids=None
):
    if not asset_ids or not vendor_ids or not process_ids:
        raise ValueError("Valid IDs required for assets, vendors and processes")

    statuses = ["Completed", "Failed", "In Progress"]

    operations = []
    for _ in range(num_operations):
        days_ago = random.randint(1, 120)
        operation_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        operations.append({
            "asset_id": random.choice(asset_ids),
            "vendor_id": random.choice(vendor_ids),
            "process_id": random.choice(process_ids),
            "operation_date": operation_date,
            "actual_cost": round(random.uniform(400, 7000), 2),
            "status": random.choice(statuses)
        })

    return operations


# =========================
# DATABASE
# =========================
def database():
    print("🚀 Seeding SmartOps AI database...")

    try:
        # 1️⃣ Business Units
        units = generate_business_units(3)
        response = supabase.table("business_units").insert(units).execute()
        unit_ids = [u["id"] for u in response.data]

        # 2️⃣ Assets
        asset_ids = []
        for unit_id in unit_ids:
            assets = generate_assets(40, unit_id)
            response = supabase.table("assets").insert(assets).execute()
            asset_ids.extend([a["id"] for a in response.data])

        # 3️⃣ Vendors
        vendors = generate_vendors(5)
        response = supabase.table("vendors").insert(vendors).execute()
        vendor_ids = [v["id"] for v in response.data]

        # 4️⃣ Processes
        processes = generate_processes(4)
        response = supabase.table("processes").insert(processes).execute()
        process_ids = [p["id"] for p in response.data]

        # 5️⃣ Operations
        operations = generate_operations(
            250, asset_ids, vendor_ids, process_ids
        )
        response = supabase.table("operations").insert(operations).execute()

        print("✅ SmartOps AI database seeded successfully")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        raise


if __name__ == "__main__":
    database()
