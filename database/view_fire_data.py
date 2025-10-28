"""
🔥 FIRE DETECTION DATABASE VIEWER
Xem dữ liệu cảm biến báo cháy từ SQLite database (fire_data.db)
"""

import sqlite3
from datetime import datetime, timedelta
import sys

DB_FILE = "fire_data.db"

# ======================= HEADER =======================
def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

# ======================= VIEW FIRE LOGS =======================
def view_fire_logs(limit=20):
    """Hiển thị các bản ghi báo cháy gần nhất"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, temperature, humidity, smoke, risk, level
        FROM fire_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()

    print_header(f"🔥 FIRE LOGS (Latest {limit} records)")
    print(f"{'Time':<20} {'Temp(°C)':<10} {'Hum(%)':<10} {'Smoke':<10} {'Risk':<6} {'Level':<10}")
    print("-"*80)

    for row in rows:
        timestamp, temp, hum, smoke, risk, level = row
        temp_str = f"{temp:.1f}" if temp is not None else "N/A"
        hum_str = f"{hum:.1f}" if hum is not None else "N/A"
        print(f"{timestamp:<20} {temp_str:<10} {hum_str:<10} "
              f"{smoke if smoke is not None else 'N/A':<10} "
              f"{risk if risk is not None else 'N/A':<6} "
              f"{level or 'N/A':<10}")

    print(f"\nTotal records: {len(rows)}")

# ======================= STATISTICS =======================
def view_statistics():
    """Thống kê tổng quan dữ liệu báo cháy"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print_header("📊 FIRE DATA STATISTICS")

    # Tổng số bản ghi
    cursor.execute("SELECT COUNT(*) FROM fire_logs")
    total = cursor.fetchone()[0]
    print(f"📦 Total records: {total}")

    # Thống kê 24h gần nhất
    cursor.execute("""
        SELECT 
            AVG(temperature), MAX(temperature), MIN(temperature),
            AVG(humidity), AVG(smoke),
            SUM(CASE WHEN level='danger' THEN 1 ELSE 0 END),
            SUM(CASE WHEN level='warning' THEN 1 ELSE 0 END)
        FROM fire_logs
        WHERE timestamp > datetime('now', '-24 hours')
    """)
    row = cursor.fetchone()
    if row and any(row):
        avg_temp, max_temp, min_temp, avg_hum, avg_smoke, danger_cnt, warn_cnt = row
        print(f"\n⏰ Last 24 hours:")
        print(f"  • Avg Temp:   {avg_temp:.1f}°C")
        print(f"  • Max Temp:   {max_temp:.1f}°C")
        print(f"  • Min Temp:   {min_temp:.1f}°C")
        print(f"  • Avg Humid:  {avg_hum:.1f}%")
        print(f"  • Avg Smoke:  {avg_smoke:.0f}")
        print(f"  • Warnings:   {warn_cnt or 0}")
        print(f"  • Dangers:    {danger_cnt or 0}")
    else:
        print("\n⚠️  No data in last 24 hours.")

    # Thống kê theo cấp độ cảnh báo
    cursor.execute("""
        SELECT level, COUNT(*) 
        FROM fire_logs
        GROUP BY level
    """)
    rows = cursor.fetchall()
    if rows:
        print(f"\n🚨 Level Summary:")
        print(f"{'Level':<10} {'Count':<10}")
        print("-"*25)
        for level, count in rows:
            print(f"{level:<10} {count:<10}")

    conn.close()

# ======================= MENU =======================
def interactive_menu():
    while True:
        print("\n" + "="*80)
        print("  🔥 FIRE DETECTION DATABASE VIEWER")
        print("="*80)
        print("[1] View Fire Logs")
        print("[2] View Statistics")
        print("[3] View All (Logs + Stats)")
        print("[0] Exit")

        choice = input("\nSelect option (0-3): ").strip()
        if choice == '1':
            limit = input("How many records? (default 20): ").strip() or "20"
            view_fire_logs(int(limit))
        elif choice == '2':
            view_statistics()
        elif choice == '3':
            view_statistics()
            view_fire_logs(10)
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option!")

# ======================= MAIN =======================
def main():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.close()
    except Exception as e:
        print(f"❌ Cannot open database: {e}")
        print(f"Make sure '{DB_FILE}' exists. Run fire_logger.py first!")
        return

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == 'logs':
            view_fire_logs()
        elif cmd == 'stats':
            view_statistics()
        elif cmd == 'all':
            view_statistics()
            view_fire_logs(10)
        else:
            print("Usage: python view_fire_data.py [logs|stats|all]")
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
