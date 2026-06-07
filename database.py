import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent / "fitness_tracker.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            notes TEXT,
            volume REAL GENERATED ALWAYS AS (sets * reps * weight) STORED,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS diet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_item TEXT NOT NULL,
            quantity TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


def add_workout(date, exercise, sets, reps, weight, notes):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO workouts (date, exercise, sets, reps, weight, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (date, exercise, sets, reps, weight, notes),
    )
    conn.commit()
    conn.close()


def add_diet(date, meal_type, food_item, quantity, calories, protein, carbs, fat, notes):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO diet
        (date, meal_type, food_item, quantity, calories, protein, carbs, fat, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (date, meal_type, food_item, quantity, calories, protein, carbs, fat, notes),
    )
    conn.commit()
    conn.close()


def get_workouts():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id, date, exercise, sets, reps, weight, volume, notes
        FROM workouts
        ORDER BY date DESC, id DESC
        """,
        conn,
    )
    conn.close()
    return df


def get_diet():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id, date, meal_type, food_item, quantity, calories, protein, carbs, fat, notes
        FROM diet
        ORDER BY date DESC, id DESC
        """,
        conn,
    )
    conn.close()
    return df


def update_workouts(df):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            UPDATE workouts
            SET date = ?, exercise = ?, sets = ?, reps = ?, weight = ?, notes = ?
            WHERE id = ?
            """,
            (
                str(row["date"]),
                row["exercise"],
                int(row["sets"]),
                int(row["reps"]),
                float(row["weight"]),
                row.get("notes", ""),
                int(row["id"]),
            ),
        )

    conn.commit()
    conn.close()


def update_diet(df):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            UPDATE diet
            SET date = ?, meal_type = ?, food_item = ?, quantity = ?,
                calories = ?, protein = ?, carbs = ?, fat = ?, notes = ?
            WHERE id = ?
            """,
            (
                str(row["date"]),
                row["meal_type"],
                row["food_item"],
                row.get("quantity", ""),
                float(row["calories"]) if pd.notna(row["calories"]) else None,
                float(row["protein"]) if pd.notna(row["protein"]) else None,
                float(row["carbs"]) if pd.notna(row["carbs"]) else None,
                float(row["fat"]) if pd.notna(row["fat"]) else None,
                row.get("notes", ""),
                int(row["id"]),
            ),
        )

    conn.commit()
    conn.close()
