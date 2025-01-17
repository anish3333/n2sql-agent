# db_setup.py
import sqlite3
from sqlite3 import Error

def create_connection():
    try:
        conn = sqlite3.connect('company.db')
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

def create_tables(conn):
    try:
        cursor = conn.cursor()
        
        # Create employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date DATE NOT NULL
            )
        ''')
        
        # Insert sample data
        sample_data = [
            (1, 'John Doe', 'Engineering', 85000, '2023-01-15'),
            (2, 'Jane Smith', 'Marketing', 75000, '2023-02-20'),
            (3, 'Bob Wilson', 'Engineering', 90000, '2023-03-10'),
            (4, 'Alice Brown', 'HR', 65000, '2023-04-05'),
            (5, 'Charlie Davis', 'Marketing', 70000, '2023-05-12')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO employees (id, name, department, salary, hire_date)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_data)
        
        conn.commit()
        print("Database initialized successfully")
    except Error as e:
        print(f"Error: {e}")

def main():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()

if __name__ == '__main__':
    main()