from datetime import date
from basecampbuddy.gear_item import GearItem

# In-memory gear list
gear_inventory = []

def add_item():
    name = input("Enter gear name: ")
    purchase_str = input("Enter purchase date (YYYY-MM-DD): ")
    purchase_date = date.fromisoformat(purchase_str)
    lifespan = int(input("Enter lifespan in years: "))
    item = GearItem(name, purchase_date, lifespan)
    gear_inventory.append(item)
    print(f"Added: {item}")

def list_items():
    if not gear_inventory:
        print("No gear in inventory.")
        return
    for idx, item in enumerate(gear_inventory, 1):
        status = "Expired" if item.is_expired() else "OK"
        check_status = "Needs check" if item.needs_check() else "Checked"
        print(f"{idx}. {item.name} - Status: {status}, Check: {check_status}")

def check_item():
    list_items()
    idx = int(input("Enter number of item to check: ")) - 1
    if 0 <= idx < len(gear_inventory):
        gear_inventory[idx].check()
        print(f"{gear_inventory[idx].name} checked today.")
    else:
        print("Invalid selection.")

def main():
    while True:
        print("\nBasecampBuddy - Gear Inventory")
        print("1. Add item")
        print("2. List items")
        print("3. Check item")
        print("4. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            add_item()
        elif choice == "2":
            list_items()
        elif choice == "3":
            check_item()
        elif choice == "4":
            print("Exiting BasecampBuddy.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()

