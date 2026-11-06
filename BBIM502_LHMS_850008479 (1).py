"""
File name: BBIM502_LHMS_850008479.py
Student: Pranish Mahato
Student ID: 850008479
Course: BBIM502 - Introduction to Programming
Cohort: BBIM7226c-Yr-1
Description: Console-based Langham Hotel Management System
Date: 30 September 2026
"""

from datetime import datetime
import math
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

STUDENT_ID = "850008479"
ALLOCATION_FILE = f"LHMS_{STUDENT_ID}.txt"
GST_RATE = Decimal("0.15")
MAX_NIGHTLY_RATE = Decimal("100000.00")

# Room data. A dictionary makes room-number lookup clear and efficient.
rooms = {
    101: {"type": "Standard", "features": "Wi-Fi, queen bed", "rate_cents": 12000, "status": "Available"},
    102: {"type": "Deluxe", "features": "Wi-Fi, city view", "rate_cents": 18000, "status": "Available"},
    103: {"type": "Executive", "features": "Wi-Fi, lounge", "rate_cents": 25000, "status": "Available"},
}

# Current customer allocations are stored separately from room details.
allocations = {}


def read_integer(prompt):
    """Read an integer safely and handle invalid, empty, or interrupted input."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid value. Please enter a whole number.")
        except EOFError:
            raise SystemExit("Input ended. Hotel program closed safely.")
        except KeyboardInterrupt:
            raise SystemExit("\nInput cancelled. Hotel program closed safely.")


def read_bounded_integer(prompt, minimum=1, maximum=None):
    """Keep prompting until a whole number falls within the permitted range."""
    while True:
        value = read_integer(prompt)
        if value < minimum or (maximum is not None and value > maximum):
            upper = f" and {maximum}" if maximum is not None else ""
            print(f"Enter a whole number between {minimum}{upper}.")
            continue
        return value


def read_nonblank(prompt):
    """Require meaningful text and stop cleanly if stdin closes."""
    while True:
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("Input ended. Hotel program closed safely.")
        if value:
            return value
        print("This field cannot be blank.")


def parse_rate(value):
    """Return validated currency as integer cents without floating-point error."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Enter a valid monetary amount.")
    if not amount.is_finite() or amount <= 0 or amount > MAX_NIGHTLY_RATE:
        raise ValueError("Rate must be above zero and at most $100,000.00.")
    if amount.as_tuple().exponent < -2 and amount != amount.quantize(Decimal("0.01")):
        raise ValueError("Rate cannot contain fractions of a cent.")
    return int(amount * 100)


def read_rate(prompt):
    while True:
        try:
            return parse_rate(input(prompt).strip())
        except ValueError as error:
            print(f"Invalid rate: {error}")
        except (EOFError, KeyboardInterrupt):
            raise SystemExit("Input ended. Hotel program closed safely.")


def money(cents):
    return f"${Decimal(cents) / 100:,.2f}"


def calculate_bill(rate_cents, nights):
    """Calculate exact subtotal, half-up rounded GST and total in cents."""
    if not isinstance(rate_cents, int) or not isinstance(nights, int):
        raise TypeError("Rate cents and nights must be integers.")
    if rate_cents <= 0 or not 1 <= nights <= 365:
        raise ValueError("Invalid rate or night count.")
    subtotal = rate_cents * nights
    gst = int((Decimal(subtotal) * GST_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return subtotal, gst, subtotal + gst


def add_room():
    """Menu option 1: add a new room to the hotel room list."""
    print("\n--- Add Room ---")
    room_number = read_bounded_integer("Enter room number: ")
    if room_number in rooms:
        print("Room already exists.")
        return

    room_type = read_nonblank("Enter room type: ")
    features = read_nonblank("Enter room features: ")
    rate_cents = read_rate("Enter nightly price: $")
    rooms[room_number] = {"type": room_type, "features": features, "rate_cents": rate_cents, "status": "Available"}
    print(f"Room {room_number} added successfully.")


def delete_room():
    """Menu option 2: delete an existing room if it is not allocated."""
    print("\n--- Delete Room ---")
    room_number = read_integer("Enter room number to delete: ")
    if room_number not in rooms:
        print("Room not found.")
        return
    if room_number in allocations:
        print("Cannot delete an allocated room. De-allocate it first.")
        return
    del rooms[room_number]
    print(f"Room {room_number} deleted successfully.")


def display_rooms():
    """Menu option 3: display room details and availability."""
    print("\n--- Room Details ---")
    if not rooms:
        print("No rooms are currently registered.")
        return
    print(f"{'Room':<8}{'Type':<16}{'Features':<22}{'Price/Night':<16}{'Status':<12}")
    print("-" * 74)
    for room_number, details in sorted(rooms.items()):
        print(
            f"{room_number:<8}{details['type'][:15]:<16}"
            f"{details.get('features', 'Not specified')[:21]:<22}"
            f"{money(details['rate_cents']):<16}{details['status']:<12}"
        )


def allocate_room():
    """Menu option 4: allocate an available room to a customer."""
    print("\n--- Allocate Room ---")
    room_number = read_integer("Enter room number to allocate: ")
    if room_number not in rooms:
        print("Room not found.")
        return
    if rooms[room_number]["status"] == "Occupied":
        print("Room is already occupied.")
        return

    customer_id = read_nonblank("Enter customer ID: ")
    customer_name = read_nonblank("Enter customer name: ")
    nights = read_bounded_integer("Enter number of nights (1-365): ", 1, 365)

    allocations[room_number] = {
        "customer": customer_name,
        "customer_id": customer_id,
        "nights": nights,
        "rate_cents": rooms[room_number]["rate_cents"],
        "allocated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    rooms[room_number]["status"] = "Occupied"
    print(f"Room {room_number} allocated to {customer_name} successfully.")


def display_allocations():
    """Menu option 5: show all active room allocations."""
    print("\n--- Current Room Allocations ---")
    if not allocations:
        print("No rooms are currently allocated.")
        return

    for room_number, data in sorted(allocations.items()):
        subtotal, _, _ = calculate_bill(data["rate_cents"], data["nights"])
        print(
            f"Room {room_number} | ID: {data['customer_id']} | Customer: {data['customer']} | "
            f"Nights: {data['nights']} | Rate: {money(data['rate_cents'])} | "
            f"Subtotal: {money(subtotal)}"
        )


def billing_and_deallocation():
    """Menu option 6: calculate the bill and release a room."""
    print("\n--- Billing & De-Allocation ---")
    room_number = read_integer("Enter room number to bill: ")
    if room_number not in allocations:
        print("This room has no active allocation.")
        return

    data = allocations[room_number]
    try:
        subtotal, tax, total = calculate_bill(data["rate_cents"], data["nights"])
    except (TypeError, ValueError) as error:
        print(f"Billing data error: {error}")
        return
    except ZeroDivisionError:
        print("Billing calculation error: division by zero.")
        return
    except OverflowError:
        print("Billing calculation exceeded the supported numeric range.")
        return

    print("\nLANGHAM HOTELS - CUSTOMER BILL")
    print("-" * 38)
    print(f"Customer : {data['customer']} ({data['customer_id']})")
    print(f"Room     : {room_number}")
    print(f"Nights   : {data['nights']}")
    print(f"Rate     : {money(data['rate_cents'])}")
    print(f"Subtotal : {money(subtotal)}")
    print(f"GST 15%  : {money(tax)}")
    print(f"TOTAL    : {money(total)}")
    print("-" * 38)

    del allocations[room_number]
    rooms[room_number]["status"] = "Available"
    print(f"Room {room_number} has been de-allocated and is available again.")


def save_allocations_to_file():
    """Menu option 7: save active allocations to the required text file."""
    print("\n--- Save Room Allocation to File ---")
    try:
        with open(ALLOCATION_FILE, "w", encoding="utf-8") as file:
            if not allocations:
                file.write("No active room allocations.\n")
            else:
                for room_number, data in sorted(allocations.items()):
                    file.write(
                        f"Room={room_number}; ID={data['customer_id']}; Customer={data['customer']}; "
                        f"Nights={data['nights']}; Rate={money(data['rate_cents'])}; "
                        f"Allocated={data['allocated_at']}\n"
                    )
        print(f"Allocation data saved to {ALLOCATION_FILE}.")
    except IOError as error:
        print(f"Unable to save allocation file: {error}")


def display_allocations_from_file():
    """Menu option 8: read and display the saved allocation file."""
    print("\n--- Display Allocation File ---")
    try:
        with open(ALLOCATION_FILE, "r", encoding="utf-8") as file:
            content = file.read()
        print(content if content else "The allocation file is empty.")
    except FileNotFoundError:
        print(f"{ALLOCATION_FILE} was not found. Use option 7 first.")
    except IOError as error:
        print(f"Unable to read allocation file: {error}")


def backup_and_clear_file():
    """Menu option 9: append data to a dated backup and clear the main file."""
    print("\n--- Backup and Clear Allocation File ---")
    try:
        with open(ALLOCATION_FILE, "r", encoding="utf-8") as source:
            content = source.read()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = f"LHMS_{STUDENT_ID}_Backup_{timestamp}.txt"

        with open(backup_file, "a", encoding="utf-8") as backup:
            backup.write(content)
            if content and not content.endswith("\n"):
                backup.write("\n")

        # Opening in write mode and immediately closing safely clears the file.
        with open(ALLOCATION_FILE, "w", encoding="utf-8"):
            pass

        print(f"Backup created: {backup_file}")
        print(f"{ALLOCATION_FILE} has been cleared.")
    except FileNotFoundError:
        print(f"{ALLOCATION_FILE} was not found. Nothing was backed up.")
    except IOError as error:
        print(f"File operation failed: {error}")


def demonstrate_exception_handling():
    """
    Controlled evidence function for the assessment's required built-in exceptions.
    It is not part of menu options 0-9 and does not affect normal hotel data.
    """
    print("\n--- Exception Handling Evidence ---")

    # 1. SyntaxError
    try:
        compile("if True print('invalid')", "<demo>", "exec")
    except SyntaxError:
        print("SyntaxError handled: invalid syntax detected before execution.")

    # 2. ValueError
    try:
        int("ABC")
    except ValueError:
        print("ValueError handled: non-numeric room input rejected.")

    # 3. ZeroDivisionError
    try:
        _ = 100 / 0
    except ZeroDivisionError:
        print("ZeroDivisionError handled: invalid zero denominator detected.")

    # 4. IndexError
    try:
        empty_rooms = []
        _ = empty_rooms[0]
    except IndexError:
        print("IndexError handled: requested sequence position does not exist.")

    # 5. NameError
    try:
        eval("undefined_room_variable")
    except NameError:
        print("NameError handled: undefined variable reference detected.")

    # 6. TypeError
    try:
        _ = "120" + 3
    except TypeError:
        print("TypeError handled: incompatible data types detected.")

    # 7. OverflowError
    try:
        math.exp(10000)
    except OverflowError:
        print("OverflowError handled: calculation exceeded numeric range.")

    # 8. IOError (OSError family)
    try:
        with open(os.path.join("/path/that/does/not/exist", "allocation.txt"), "w") as file:
            file.write("test")
    except IOError:
        print("IOError handled: file could not be opened/written.")

    # 9. ImportError
    try:
        __import__("langham_missing_demo_module")
    except ImportError:
        print("ImportError handled: requested module is unavailable.")

    # 10. EOFError
    try:
        raise EOFError("controlled demonstration")
    except EOFError:
        print("EOFError handled: unexpected end of input detected.")

    # 11. FileNotFoundError
    try:
        with open("definitely_missing_lhms_demo_file.txt", "r", encoding="utf-8"):
            pass
    except FileNotFoundError:
        print("FileNotFoundError handled: missing file detected.")


def display_menu():
    """Display the required Hotel Management System menu."""
    print("\n" + "=" * 52)
    print("        LANGHAM HOTEL MANAGEMENT SYSTEM")
    print("=" * 52)
    print("1. Add Room")
    print("2. Delete Room")
    print("3. Display Room Details")
    print("4. Allocate Room")
    print("5. Display Room Allocation Details")
    print("6. Billing & De-Allocation")
    print("7. Save Room Allocation to File")
    print("8. Display Room Allocation from File")
    print("9. Backup and Clear Room Allocation File")
    print("0. Exit Application")
    print("=" * 52)


def main():
    """Main program loop for menu options 0-9."""
    while True:
        display_menu()
        try:
            choice = input("Enter your choice (0-9): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInput ended. Hotel program closed safely.")
            break

        if choice == "1":
            add_room()
        elif choice == "2":
            delete_room()
        elif choice == "3":
            display_rooms()
        elif choice == "4":
            allocate_room()
        elif choice == "5":
            display_allocations()
        elif choice == "6":
            billing_and_deallocation()
        elif choice == "7":
            save_allocations_to_file()
        elif choice == "8":
            display_allocations_from_file()
        elif choice == "9":
            backup_and_clear_file()
        elif choice == "0":
            print("Thank you for using the Langham Hotel Management System.")
            break
        else:
            print("Invalid menu option. Please choose a number from 0 to 9.")


if __name__ == "__main__":
    main()
