from src.config import DATABASE_URL
from src.db import get_db, init_db

def main():
    conn = get_db(DATABASE_URL)
    init_db(conn)
    print(f"Initialized DB at {DATABASE_URL}")

if __name__ == "__main__":
    main()