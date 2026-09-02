import sqlite3
import json

DB_PATH = "report.db"

def get_report_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Total number of orders
    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]

    # 2. Total revenue
    cur.execute("SELECT ROUND(COALESCE(SUM(amount), 0), 2) FROM orders")
    total_revenue = cur.fetchone()[0]

    # 3. Top 5 products by revenue
    cur.execute("""
        SELECT product, ROUND(SUM(amount), 2) as revenue, COUNT(*) as count
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
    """)
    top_products = [
        {"product": row[0], "revenue": row[1], "count": row[2]}
        for row in cur.fetchall()
    ]

    # 4. Orders per day for the last 7 days
    cur.execute("""
        SELECT created_at, COUNT(*), ROUND(SUM(amount), 2)
        FROM orders
        GROUP BY created_at
        ORDER BY created_at DESC
        LIMIT 7
    """)
    orders_last_7_days = [
        {"date": row[0], "order_count": row[1], "revenue": row[2]}
        for row in cur.fetchall()
    ]

    # Fetch all orders to test the multi-page table break
    cur.execute("SELECT id, customer, product, amount, created_at FROM orders ORDER BY created_at DESC")
    all_orders = [
        {"id": row[0], "customer": row[1], "product": row[2], "amount": row[3], "created_at": row[4]}
        for row in cur.fetchall()
    ]

    conn.close()

    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "top_products": top_products,
        "orders_last_7_days": orders_last_7_days,
        "all_orders": all_orders
    }

if __name__ == "__main__":
    data = get_report_data()
    # This will print summary structure
    print(json.dumps({
        "total_orders": data["total_orders"],
        "total_revenue": data["total_revenue"],
        "top_products": data["top_products"],
        "orders_last_7_days": data["orders_last_7_days"]
    }, indent=2))
