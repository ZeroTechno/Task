import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from report_data import get_report_data

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def build_html(data):
    today = datetime.now().strftime("%B %d, %Y")

    top_products_rows = "".join([
        f"<tr><td>{p['product']}</td><td>{p['count']}</td><td>${p['revenue']:,.2f}</td></tr>"
        for p in data["top_products"]
    ])

    daily_rows = "".join([
        f"<tr><td>{d['date']}</td><td>{d['order_count']}</td><td>${d['revenue']:,.2f}</td></tr>"
        for d in data["orders_last_7_days"]
    ])

    all_orders_rows = "".join([
        f"<tr><td>#{o['id']}</td><td>{o['customer']}</td><td>{o['product']}</td><td>${o['amount']:,.2f}</td><td>{o['created_at']}</td></tr>"
        for o in data["all_orders"]
    ])

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Sales & Operations Report</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 15mm 20mm 15mm;
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1a202c;
        line-height: 1.5;
        padding: 0;
        margin: 0;
    }}
    h1 {{ font-size: 24px; margin-bottom: 4px; color: #111827; }}
    .date {{ font-size: 13px; color: #6b7280; margin-bottom: 24px; }}
    .cards {{ display: flex; gap: 16px; margin-bottom: 28px; }}
    .card {{
        flex: 1;
        padding: 16px;
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }}
    .card-label {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: #6b7280; }}
    .card-value {{ font-size: 22px; font-weight: 700; color: #1f2937; margin-top: 4px; }}
    h2 {{ font-size: 16px; margin-top: 24px; margin-bottom: 12px; color: #374151; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 24px;
        font-size: 12px;
    }}
    th, td {{
        padding: 8px 12px;
        text-align: left;
        border-bottom: 1px solid #e5e7eb;
    }}
    th {{
        background-color: #f3f4f6;
        font-weight: 600;
        color: #4b5563;
    }}
    /* Print CSS fixes for clean page breaks */
    thead {{
        display: table-header-group; /* Repeats table header across pages */
    }}
    tr {{
        break-inside: avoid;         /* Prevents rows from getting cut in half */
        page-break-inside: avoid;
    }}
</style>
</head>
<body>
    <h1>Sales & Operations Report</h1>
    <div class="date">Generated on {today}</div>

    <div class="cards">
        <div class="card">
            <div class="card-label">Total Orders</div>
            <div class="card-value">{data['total_orders']}</div>
        </div>
        <div class="card">
            <div class="card-label">Total Revenue</div>
            <div class="card-value">${data['total_revenue']:,.2f}</div>
        </div>
    </div>

    <h2>Top 5 Products by Revenue</h2>
    <table>
        <thead>
            <tr><th>Product</th><th>Orders</th><th>Revenue</th></tr>
        </thead>
        <tbody>
            {top_products_rows}
        </tbody>
    </table>

    <h2>Recent 7-Day Performance</h2>
    <table>
        <thead>
            <tr><th>Date</th><th>Orders</th><th>Revenue</th></tr>
        </thead>
        <tbody>
            {daily_rows}
        </tbody>
    </table>

    <h2>All Orders Log ({len(data['all_orders'])} records)</h2>
    <table>
        <thead>
            <tr><th>ID</th><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr>
        </thead>
        <tbody>
            {all_orders_rows}
        </tbody>
    </table>
</body>
</html>"""

async def generate_pdf(output_path="reports/test.pdf"):
    data = get_report_data()
    html = build_html(data)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")
        await page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"}
        )
        await browser.close()
    
    print(f"Report generated successfully: {output_path}")

if __name__ == "__main__":
    asyncio.run(generate_pdf())
