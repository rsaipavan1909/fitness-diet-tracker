import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
import bcrypt


def get_connection():
    return psycopg2.connect(st.secrets["SUPABASE_DB_URL"])


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)


def create_user(name, username, password):
    conn = get_connection()
    cur = conn.cursor()

    username = username.lower().strip()
    password_hash = hash_password(password)

    try:
        cur.execute(
            """
            INSERT INTO app_users (name, username, email, password_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (
                name.strip(),
                username,
                f"{username}@fitness.local",
                password_hash,
            ),
        )
        conn.commit()
        return True, "Account created successfully."

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, "This username is already taken."

    except Exception as e:
        conn.rollback()
        return False, f"Signup error: {e}"

    finally:
        cur.close()
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    username = username.lower().strip()

    cur.execute(
        """
        SELECT id, name, username, password_hash
        FROM app_users
        WHERE username = %s
        """,
        (username,),
    )

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        return False, None, "Invalid username or password."

    if verify_password(password, user["password_hash"]):
        return True, user, "Login successful."

    return False, None, "Invalid username or password."


def add_workout(user_id, date, exercise, sets, reps, weight, notes):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO workouts (user_id, date, exercise, sets, reps, weight, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, date, exercise, sets, reps, weight, notes),
    )

    conn.commit()
    cur.close()
    conn.close()


def add_diet(user_id, date, meal_type, food_item, quantity, calories, protein, carbs, fat, notes):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO diet
        (user_id, date, meal_type, food_item, quantity, calories, protein, carbs, fat, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            date,
            meal_type,
            food_item,
            quantity,
            calories,
            protein,
            carbs,
            fat,
            notes,
        ),
    )

    conn.commit()
    cur.close()
    conn.close()


def get_workouts(user_id):
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT id, date, exercise, sets, reps, weight, volume, notes
        FROM workouts
        WHERE user_id = %s
        ORDER BY date DESC, id DESC
        """,
        conn,
        params=(user_id,),
    )

    conn.close()
    return df


def get_diet(user_id):
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT id, date, meal_type, food_item, quantity, calories, protein, carbs, fat, notes
        FROM diet
        WHERE user_id = %s
        ORDER BY date DESC, id DESC
        """,
        conn,
        params=(user_id,),
    )

    conn.close()
    return df


def update_workouts(user_id, df):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            UPDATE workouts
            SET date = %s,
                exercise = %s,
                sets = %s,
                reps = %s,
                weight = %s,
                notes = %s
            WHERE id = %s AND user_id = %s
            """,
            (
                row["date"],
                row["exercise"],
                int(row["sets"]),
                int(row["reps"]),
                float(row["weight"]),
                row.get("notes", ""),
                int(row["id"]),
                user_id,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def update_diet(user_id, df):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute(
            """
            UPDATE diet
            SET date = %s,
                meal_type = %s,
                food_item = %s,
                quantity = %s,
                calories = %s,
                protein = %s,
                carbs = %s,
                fat = %s,
                notes = %s
            WHERE id = %s AND user_id = %s
            """,
            (
                row["date"],
                row["meal_type"],
                row["food_item"],
                row.get("quantity", ""),
                float(row["calories"]) if pd.notna(row["calories"]) else None,
                float(row["protein"]) if pd.notna(row["protein"]) else None,
                float(row["carbs"]) if pd.notna(row["carbs"]) else None,
                float(row["fat"]) if pd.notna(row["fat"]) else None,
                row.get("notes", ""),
                int(row["id"]),
                user_id,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()