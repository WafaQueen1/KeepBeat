import sqlite3
import os

DB_PATH = "keepbeat_fallback.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("SQLite DB not found, skipping local migration.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Update doctors (except Sterling) to pending if they are currently approved but not Sterling
    cursor.execute("UPDATE doctors SET status = 'pending' WHERE id != 'doc_sterling_001' AND status = 'approved'")
    print(f"Updated {cursor.rowcount} doctors to pending.")

    # 2. Update patients
    cursor.execute("UPDATE patients SET status = 'pending' WHERE status = 'approved' OR status IS NULL")
    print(f"Updated {cursor.rowcount} patients to pending.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
