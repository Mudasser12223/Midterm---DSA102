"""
Restaurant Order Management System
DSA 102 - Semester Project
Student: Mudasser Qaharoghlu | 250221021104
"""

import csv
import os
from datetime import datetime


# ─────────────────────────────────────────────
#  CLASS 1: MenuItem
#  Represents a single item on the menu
# ─────────────────────────────────────────────
class MenuItem:
    def __init__(self, name, category, price):
        self.name = name
        self.category = category
        self.price = float(price)

    def display(self):
        print(f"  {self.name:<25} {self.category:<12} ${self.price:.2f}")


# ─────────────────────────────────────────────
#  CLASS 2: Menu
#  Loads and manages all menu items from CSV
# ─────────────────────────────────────────────
class Menu:
    def __init__(self, filepath):
        self.items = []  # list of MenuItem objects
        self.load_from_csv(filepath)

    def load_from_csv(self, filepath):
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = MenuItem(row["name"], row["category"], row["price"])
                self.items.append(item)
        print(f"[Menu] Loaded {len(self.items)} items.")

    def display_all(self):
        print("\n" + "=" * 50)
        print(f"  {'ITEM':<25} {'CATEGORY':<12} PRICE")
        print("=" * 50)
        for item in self.items:
            item.display()
        print("=" * 50)

    def display_by_category(self, category):
        print(f"\n--- {category.upper()} ---")
        found = False
        for item in self.items:
            if item.category.lower() == category.lower():
                item.display()
                found = True
        if not found:
            print("  No items in this category.")

    def find_item(self, name):
        # Search for an item by name (case-insensitive)
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
        return None

    def get_categories(self):
        categories = []
        for item in self.items:
            if item.category not in categories:
                categories.append(item.category)
        return categories


# ─────────────────────────────────────────────
#  CLASS 3: Table
#  Represents a physical table in the restaurant
# ─────────────────────────────────────────────
class Table:
    def __init__(self, table_number, capacity=4):
        self.table_number = table_number
        self.capacity = capacity
        self.is_occupied = False
        self.waiter_name = None

    def seat_guests(self, waiter_name):
        self.is_occupied = True
        self.waiter_name = waiter_name

    def free_table(self):
        self.is_occupied = False
        self.waiter_name = None

    def status(self):
        if self.is_occupied:
            return f"Table {self.table_number}: OCCUPIED | Waiter: {self.waiter_name}"
        else:
            return f"Table {self.table_number}: FREE"


# ─────────────────────────────────────────────
#  CLASS 4: Order
#  Belongs to a table; stores ordered items
# ─────────────────────────────────────────────
class Order:
    def __init__(self, table_number, vat_rate):
        self.table_number = table_number
        self.vat_rate = vat_rate
        self.items = []           # list of MenuItem objects
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.is_served = False

    def add_item(self, menu_item):
        self.items.append(menu_item)

    def get_subtotal(self):
        total = 0
        for item in self.items:
            total += item.price
        return total

    def get_tax(self):
        return self.get_subtotal() * self.vat_rate

    def get_total(self):
        return self.get_subtotal() + self.get_tax()

    def print_receipt(self, restaurant_name):
        print("\n" + "=" * 40)
        print(f"  {restaurant_name}")
        print(f"  Table: {self.table_number} | {self.timestamp}")
        print("=" * 40)
        for item in self.items:
            print(f"  {item.name:<22} ${item.price:.2f}")
        print("-" * 40)
        print(f"  {'Subtotal':<22} ${self.get_subtotal():.2f}")
        print(f"  {'VAT (10%)':<22} ${self.get_tax():.2f}")
        print(f"  {'TOTAL':<22} ${self.get_total():.2f}")
        print("=" * 40)


# ─────────────────────────────────────────────
#  HELPER CLASS: Node (for the linked list)
#  Each node holds one Order and a pointer to the next
# ─────────────────────────────────────────────
class Node:
    def __init__(self, order):
        self.order = order   # the Order object
        self.next = None     # pointer to the next Node


# ─────────────────────────────────────────────
#  CLASS 5: OrderQueue
#  A custom FIFO queue built with a singly linked list
#  - enqueue() adds to the tail (new orders go to end)
#  - dequeue() removes from the head (oldest order served first)
# ─────────────────────────────────────────────
class OrderQueue:
    def __init__(self):
        self.head = None   # front of the queue (next to be served)
        self.tail = None   # back of the queue (most recently added)
        self.size = 0

    def is_empty(self):
        return self.head is None

    def enqueue(self, order):
        new_node = Node(order)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node  # link old tail to new node
            self.tail = new_node       # update tail pointer
        self.size += 1
        print(f"[Queue] Order for Table {order.table_number} added to kitchen queue.")

    def dequeue(self):
        if self.is_empty():
            print("[Queue] No orders in queue.")
            return None
        order = self.head.order    # get the order from the front
        self.head = self.head.next # move head forward
        if self.head is None:
            self.tail = None       # queue is now empty
        self.size -= 1
        return order

    def display_queue(self):
        if self.is_empty():
            print("  Kitchen queue is empty.")
            return
        print(f"\n  Kitchen Queue ({self.size} order(s)):")
        current = self.head
        position = 1
        while current is not None:
            status = "SERVED" if current.order.is_served else "WAITING"
            print(f"  [{position}] Table {current.order.table_number} | {current.order.timestamp} | {status}")
            current = current.next
            position += 1


# ─────────────────────────────────────────────
#  CLASS 6: Restaurant (Main Controller)
#  Manages everything and runs the CLI loop
# ─────────────────────────────────────────────
class Restaurant:
    def __init__(self, config_path, menu_path):
        self.config = self.load_config(config_path)
        self.name = self.config.get("restaurant_name", "My Restaurant")
        self.vat_rate = float(self.config.get("vat_rate", 0.10))
        self.num_tables = int(self.config.get("num_tables", 5))

        self.menu = Menu(menu_path)
        self.tables = []
        self.order_queue = OrderQueue()
        self.orders_history = []   # all orders ever placed

        # Create table objects
        for i in range(1, self.num_tables + 1):
            self.tables.append(Table(i))

        print(f"\nWelcome to {self.name}!")
        print(f"Tables: {self.num_tables} | VAT: {int(self.vat_rate * 100)}%")

    def load_config(self, filepath):
        config = {}
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
        return config

    def get_table(self, table_number):
        for table in self.tables:
            if table.table_number == table_number:
                return table
        return None

    def show_tables(self):
        print("\n--- TABLE STATUS ---")
        for table in self.tables:
            print(" ", table.status())

    def seat_table(self):
        self.show_tables()
        try:
            t_num = int(input("\nEnter table number to seat: "))
        except ValueError:
            print("Invalid input.")
            return
        table = self.get_table(t_num)
        if table is None:
            print("Table not found.")
            return
        if table.is_occupied:
            print(f"Table {t_num} is already occupied.")
            return
        waiter = input("Enter waiter name: ").strip()
        if not waiter:
            print("Waiter name cannot be empty.")
            return
        table.seat_guests(waiter)
        print(f"Table {t_num} seated. Assigned to {waiter}.")

    def take_order(self):
        self.show_tables()
        try:
            t_num = int(input("\nEnter table number to order for: "))
        except ValueError:
            print("Invalid input.")
            return
        table = self.get_table(t_num)
        if table is None:
            print("Table not found.")
            return
        if not table.is_occupied:
            print(f"Table {t_num} is not occupied yet. Please seat guests first.")
            return

        order = Order(t_num, self.vat_rate)
        self.menu.display_all()

        print("\nType item names to add (type 'done' when finished):")
        while True:
            item_name = input("  Add item: ").strip()
            if item_name.lower() == "done":
                break
            item = self.menu.find_item(item_name)
            if item:
                order.add_item(item)
                print(f"  + {item.name} added (${item.price:.2f})")
            else:
                print(f"  Item '{item_name}' not found. Try again.")

        if not order.items:
            print("No items added. Order cancelled.")
            return

        self.order_queue.enqueue(order)
        self.orders_history.append(order)
        print(f"Order placed for Table {t_num} with {len(order.items)} item(s).")

    def serve_next_order(self):
        print("\n--- SERVE NEXT ORDER ---")
        order = self.order_queue.dequeue()
        if order is None:
            return
        order.is_served = True
        print(f"Serving order for Table {order.table_number}.")
        order.print_receipt(self.name)

    def view_queue(self):
        print("\n--- KITCHEN QUEUE ---")
        self.order_queue.display_queue()

    def bill_and_clear(self):
        self.show_tables()
        try:
            t_num = int(input("\nEnter table number to bill and clear: "))
        except ValueError:
            print("Invalid input.")
            return
        table = self.get_table(t_num)
        if table is None:
            print("Table not found.")
            return
        if not table.is_occupied:
            print(f"Table {t_num} is already free.")
            return

        # Find served orders for this table and print final receipt
        served = [o for o in self.orders_history if o.table_number == t_num and o.is_served]
        if not served:
            print("No served orders found for this table. Serve the order first.")
            return

        # Combine all items from all orders for this table into one receipt
        print("\n" + "=" * 40)
        print(f"  FINAL BILL - {self.name}")
        print(f"  Table {t_num}")
        print("=" * 40)
        grand_subtotal = 0
        for order in served:
            for item in order.items:
                print(f"  {item.name:<22} ${item.price:.2f}")
                grand_subtotal += item.price
        tax = grand_subtotal * self.vat_rate
        print("-" * 40)
        print(f"  {'Subtotal':<22} ${grand_subtotal:.2f}")
        print(f"  {'VAT (10%)':<22} ${tax:.2f}")
        print(f"  {'TOTAL':<22} ${grand_subtotal + tax:.2f}")
        print("=" * 40)

        table.free_table()
        print(f"Table {t_num} has been cleared and is now free.")

    def run(self):
        while True:
            print("\n" + "=" * 40)
            print(f"  {self.name} — Main Menu")
            print("=" * 40)
            print("  1. View Tables")
            print("  2. Seat Guests at Table")
            print("  3. Take Order")
            print("  4. View Kitchen Queue")
            print("  5. Serve Next Order")
            print("  6. Print Bill & Clear Table")
            print("  7. View Full Menu")
            print("  0. Exit")
            print("=" * 40)

            choice = input("  Select option: ").strip()

            if choice == "1":
                self.show_tables()
            elif choice == "2":
                self.seat_table()
            elif choice == "3":
                self.take_order()
            elif choice == "4":
                self.view_queue()
            elif choice == "5":
                self.serve_next_order()
            elif choice == "6":
                self.bill_and_clear()
            elif choice == "7":
                self.menu.display_all()
            elif choice == "0":
                print(f"\nThank you for using {self.name} system. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, "..", "files.data", "config.txt")
    MENU_PATH = os.path.join(BASE_DIR, "..", "files.data", "menu.csv")

    restaurant = Restaurant(CONFIG_PATH, MENU_PATH)
    restaurant.run()
