import sqlite3
import pandas as pd
import os

def create_database():
    print("Creating users database...")
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        roll_no TEXT,
        name TEXT
    )
    ''')

    # Clear existing data just in case
    cursor.execute('DELETE FROM users')

    # Add Educators
    educators = [
        ("edu1", "edu1", "Educator", None, "Dr. Smith"),
        ("edu2", "edu2", "Educator", None, "Prof. Jones"),
        ("educator", "educator123", "Educator", None, "Default Educator")
    ]
    
    for ed in educators:
        cursor.execute('''
        INSERT INTO users (username, password, role, roll_no, name) 
        VALUES (?, ?, ?, ?, ?)
        ''', ed)

    print(f"Added {len(educators)} educators to the database.")

    # Add Students from Excel File
    try:
        df = pd.read_excel('student_performance_enhanced.xlsx')
        
        # We will take the first 10 students and give them simple usernames
        # username: stu1, stu2, stu3 etc.
        # password: same as username (e.g., stu1 / stu1)
        count = 0
        
        for index, row in df.head(50).iterrows(): # Let's create 50 simple logins
            roll_no = row['RollNo']
            username = f"stu{index + 1}"
            password = username # Super simple password
            name = f"Student {index + 1}"
            
            cursor.execute('''
            INSERT INTO users (username, password, role, roll_no, name) 
            VALUES (?, ?, ?, ?, ?)
            ''', (username, password, "Student", roll_no, name))
            count += 1
            
        print(f"Added {count} simple student logins to the database.")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        # Insert a fallback student if excel reading fails
        cursor.execute('''
        INSERT INTO users (username, password, role, roll_no, name) 
        VALUES (?, ?, ?, ?, ?)
        ''', ("stu1", "stu1", "Student", "STU1000", "John Fallback"))

    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_database()
