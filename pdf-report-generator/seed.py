import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "report.db"

PRODUCTS = [
    "Mechanical Keyboard",
    "Ergonomic Mouse",
    "4K Monitor",
    "USB-C Dock",
    "Noise Canceling Headphones",
    "Desk Pad"
]

CUSTOMERS = [
    "Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince",
    "Evan Wright", "Fiona Gallagher", "George Clark", "Hannah Abbott"
]

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at DATE NOT NULL
        )
    """)

    # Clear existing rows so seeding twice leaves exactly 200 rows
    cur.execute("DELETE FROM orders")

    now = datetime.now()
    orders = []
    for _ in range(200):
        cust = random.choice(CUSTOMERS)
        prod = random.choice(PRODUCTS)
        amt = round(random.uniform(15.0, 350.0), 2)
        days_ago = random.randint(0, 29)
        order_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        orders.append((cust, prod, amt, order_date))

    cur.executemany(
        "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)",
        orders
    )

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM orders")
    count = cur.fetchone()[0]
    conn.close()
    print(f"Seeded successfully. Total orders: {count}")

if __name__ == "__main__":
    seed_database()
