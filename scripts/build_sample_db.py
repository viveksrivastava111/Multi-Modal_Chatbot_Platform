"""
Run this once to (re)generate the sample e-commerce SQLite database
used by the SQL Query Assistant module out of the box.

    python scripts/build_sample_db.py
"""
import os
import sqlite3
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "sample.db")

random.seed(42)

CATEGORIES = ["Electronics", "Home & Kitchen", "Books", "Clothing", "Sports", "Toys"]
CUSTOMER_NAMES = [
    "Aarav Sharma", "Priya Verma", "Rohan Gupta", "Ananya Singh", "Vivaan Mehta",
    "Isha Kapoor", "Kabir Nair", "Diya Reddy", "Arjun Rao", "Saanvi Joshi",
]


def build():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            signup_date TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Hyderabad", "Chennai"]
    for i, name in enumerate(CUSTOMER_NAMES, start=1):
        cur.execute(
            "INSERT INTO customers VALUES (?, ?, ?, ?)",
            (i, name, random.choice(cities), f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"),
        )

    products = [
        ("Wireless Earbuds", "Electronics", 1999.0),
        ("Smart Watch", "Electronics", 3499.0),
        ("Non-stick Pan Set", "Home & Kitchen", 1299.0),
        ("Air Fryer", "Home & Kitchen", 4999.0),
        ("Data Structures Textbook", "Books", 599.0),
        ("Sci-Fi Novel", "Books", 349.0),
        ("Running Shoes", "Sports", 2499.0),
        ("Yoga Mat", "Sports", 899.0),
        ("Denim Jacket", "Clothing", 1799.0),
        ("Cotton T-Shirt", "Clothing", 499.0),
        ("Building Blocks Set", "Toys", 999.0),
        ("RC Car", "Toys", 1599.0),
    ]
    for i, (name, cat, price) in enumerate(products, start=1):
        cur.execute("INSERT INTO products VALUES (?, ?, ?, ?)", (i, name, cat, price))

    order_id = 1
    for customer_id in range(1, len(CUSTOMER_NAMES) + 1):
        for _ in range(random.randint(2, 6)):
            product_id = random.randint(1, len(products))
            quantity = random.randint(1, 3)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            cur.execute(
                "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
                (order_id, customer_id, product_id, quantity, f"2024-{month:02d}-{day:02d}"),
            )
            order_id += 1

    conn.commit()
    conn.close()
    print(f"Sample database created at {DB_PATH}")


if __name__ == "__main__":
    build()
