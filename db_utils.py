import sqlite3
import os
from dotenv import load_dotenv
from typing import List, Tuple, Optional

load_dotenv()
DB_PATH = os.getenv("PHARMACY_DB", "pharmacy.db")

def list_tables() -> List[str]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [t[0] for t in cursor.fetchall()]

def describe_table(table_name: str) -> List[Tuple[str, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        return [(col[1], col[2]) for col in cursor.fetchall()]

def execute_query(sql: str) -> List[Tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.commit()
        return result

def get_drug_id(name: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM drugs")
        all_drugs = cursor.fetchall()
        for drug_id, drug_name in all_drugs:
            if name.replace(" ", "").lower() == drug_name.replace(" ", "").lower():
                return drug_id
        raise ValueError(f"Drug '{name}' not found in database.")

def get_available_stock(drug_id: int) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM drugs WHERE id = ?", (drug_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"No quantity entry for drug ID {drug_id}")

def insert_sale(drug_id: int, quantity: int) -> None:
    from datetime import date
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (drug_id, quantity_sold, sale_date) VALUES (?, ?, ?)",
            (drug_id, quantity, date.today())
        )
        conn.commit()

def update_stock(drug_id: int, quantity_sold: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE drugs SET quantity = quantity - ? WHERE id = ?", (quantity_sold, drug_id))
        conn.commit()

def get_inventory_info(drug_id: int) -> Optional[List]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, brand, quantity, expiry_date, price_per_unit FROM drugs WHERE id = ?",
            (drug_id,)
        )
        result = cursor.fetchone()
        return list(result) if result else None

def get_full_inventory() -> List[List]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, brand, quantity, expiry_date, price_per_unit FROM drugs")
        return [list(row) for row in cursor.fetchall()]
