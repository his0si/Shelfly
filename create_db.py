import sqlite3
import os

def create_database():
    # 기존 데이터베이스 파일이 있다면 삭제
    if os.path.exists('books.db'):
        os.remove('books.db')
        print("Removed existing database")

    # 새로운 데이터베이스 연결 생성
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    
    # users 테이블 생성
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # books 테이블 생성
    c.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            review TEXT,
            rating INTEGER,
            date_read DATE,
            user_id INTEGER,
            UNIQUE(title, author, user_id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # 변경사항 저장
    conn.commit()
    
    # 테이블이 생성되었는지 확인
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    print("Created tables:", tables)
    
    # 연결 종료
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print(f"Error creating database: {e}")