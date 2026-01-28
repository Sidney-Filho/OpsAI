from app.data import database

if __name__ == "__main__":
    print("=" * 50)
    print("  SMARTOPS AI - DATABASE")
    print("=" * 50)

    response = input(
        "\n⚠️  This will insert sample data into the SmartOps AI database.\nContinue? (yes/no): "
    )

    if response.lower() in ["yes", "y", "s", "sim"]:
        try:
            database()
        except Exception as e:
            print(f"\n💥 Seeding failed: {e}")
            exit(1)
    else:
        print("\n🚫 Seeding cancelled by user.")
        exit(0)
