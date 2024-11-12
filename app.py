from flask import Flask, render_template, request, jsonify
import sqlite3
import logging
from datetime import datetime

app = Flask(__name__)

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)

def init_db():
    try:
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        
        # 기존 테이블이 있다면 삭제
        c.execute('DROP TABLE IF EXISTS books')
        
        # 새로운 테이블 생성 (title과 author의 조합이 unique)
        c.execute('''CREATE TABLE books
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      author TEXT NOT NULL,
                      review TEXT,
                      rating INTEGER,
                      date_read DATE,
                      UNIQUE(title, author))''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database error: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        data = request.json
        print(f"Received data: {data}")
        
        # 중복 체크
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        
        # 같은 제목과 저자의 책이 이미 있는지 확인
        c.execute('''SELECT * FROM books 
                    WHERE title=? AND author=?''', 
                    (data['title'], data['author']))
        
        existing_book = c.fetchone()
        if existing_book:
            conn.close()
            return jsonify({
                "status": "error",
                "message": "이미 등록된 책입니다."
            }), 400
            
        # 중복이 아닌 경우 새로운 책 추가
        c.execute('''INSERT INTO books (title, author, review, rating, date_read)
                     VALUES (?, ?, ?, ?, ?)''',
                  (data['title'], data['author'], data['review'],
                   int(data['rating']), data['date_read']))
        conn.commit()
        conn.close()
        print("Book added successfully")
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error adding book: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_books')
def get_books():
    try:
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        c.execute('SELECT * FROM books ORDER BY date_read DESC')
        books = [{"id": row[0], "title": row[1], "author": row[2],
                  "review": row[3], "rating": row[4], "date_read": row[5]}
                 for row in c.fetchall()]
        conn.close()
        print("Retrieved books:", books)
        return jsonify(books)
    except Exception as e:
        print(f"Error getting books: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_book/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        data = request.json
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        
        # 다른 책과의 중복 체크 (자기 자신은 제외)
        c.execute('''SELECT * FROM books 
                    WHERE title=? AND author=? AND id!=?''', 
                    (data['title'], data['author'], book_id))
        existing_book = c.fetchone()
        if existing_book:
            conn.close()
            return jsonify({
                "status": "error",
                "message": "이미 등록된 책입니다."
            }), 400
            
        c.execute('''UPDATE books 
                     SET title=?, author=?, review=?, rating=?, date_read=?
                     WHERE id=?''',
                  (data['title'], data['author'], data['review'],
                   int(data['rating']), data['date_read'], book_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error updating book: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_book/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        c.execute('DELETE FROM books WHERE id=?', (book_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error deleting book: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)