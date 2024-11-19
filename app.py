from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 실제 운영시에는 안전한 키로 변경

# login_required 데코레이터 정의
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "로그인이 필요합니다."}), 401
        return f(*args, **kwargs)
    return decorated_function

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    
    # users 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL UNIQUE,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # books 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  review TEXT,
                  rating INTEGER,
                  date_read DATE,
                  user_id INTEGER,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

# 데이터베이스 연결 함수
def get_db():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row
    return conn

# 기본 라우트 (메인 페이지)
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# 회원가입 페이지
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"status": "error", "message": "모든 필드를 입력해주세요."}), 400

        conn = get_db()
        try:
            cursor = conn.cursor()
            
            # 아이디 중복 체크
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                return jsonify({"status": "error", "message": "이미 사용 중인 아이디입니다."}), 400

            # 새 사용자 등록
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                         (username, hashed_password))
            conn.commit()
            return jsonify({"status": "success", "message": "회원가입이 완료되었습니다."})
        except Exception as e:
            print(f"Registration error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            conn.close()

# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return jsonify({"status": "success", "message": "로그인 성공"})
            return jsonify({"status": "error", "message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401
        finally:
            conn.close()

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 책 추가
@app.route('/add_book', methods=['POST'])
@login_required
def add_book():
    try:
        data = request.json
        user_id = session['user_id']
        
        # 필수 필드 확인
        if not data.get('title') or not data.get('author'):
            return jsonify({
                "status": "error",
                "message": "제목과 저자는 필수 입력 항목입니다."
            }), 400

        conn = get_db()
        try:
            c = conn.cursor()
            
            # 같은 사용자의 같은 책인지 확인
            c.execute('''SELECT * FROM books 
                        WHERE title=? AND author=? AND user_id=?''', 
                        (data['title'], data['author'], user_id))
            
            if c.fetchone():
                return jsonify({
                    "status": "error",
                    "message": "이미 등록된 책입니다."
                }), 400
                
            # 책 추가
            c.execute('''INSERT INTO books 
                        (title, author, review, rating, date_read, user_id)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (data['title'], 
                      data['author'], 
                      data.get('review', ''),  # review가 없으면 빈 문자열
                      int(data.get('rating', 0)),  # rating이 없으면 0
                      data.get('date_read', ''),  # date_read가 없으면 빈 문자열
                      user_id))
            
            conn.commit()
            return jsonify({"status": "success", "message": "책이 추가되었습니다."})
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return jsonify({
                "status": "error",
                "message": f"데이터베이스 오류: {str(e)}"
            }), 500
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error adding book: {e}")
        return jsonify({
            "status": "error",
            "message": f"책 추가 중 오류가 발생했습니다: {str(e)}"
        }), 500
    
    # 책 삭제
@app.route('/delete_book/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    try:
        user_id = session['user_id']
        conn = get_db()
        try:
            cursor = conn.cursor()
            
            # 해당 책이 현재 로그인한 사용자의 것인지 확인
            cursor.execute('SELECT * FROM books WHERE id = ? AND user_id = ?', 
                         (book_id, user_id))
            book = cursor.fetchone()
            
            if not book:
                return jsonify({
                    "status": "error",
                    "message": "해당 책을 찾을 수 없거나 삭제 권한이 없습니다."
                }), 404
            
            # 책 삭제
            cursor.execute('DELETE FROM books WHERE id = ? AND user_id = ?', 
                         (book_id, user_id))
            conn.commit()
            
            return jsonify({
                "status": "success",
                "message": "책이 삭제되었습니다."
            })
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return jsonify({
                "status": "error",
                "message": f"���이터베이스 오류: {str(e)}"
            }), 500
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Error deleting book: {e}")
        return jsonify({
            "status": "error",
            "message": f"책 삭제 중 오류가 발생했습니다: {str(e)}"
        }), 500

# 책 목록 가져오기
@app.route('/get_books')
@login_required
def get_books():
    try:
        user_id = session['user_id']
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM books 
                            WHERE user_id = ? 
                            ORDER BY date_read DESC''', (user_id,))
            books = []
            for row in cursor.fetchall():
                books.append({
                    "id": row['id'],
                    "title": row['title'],
                    "author": row['author'],
                    "review": row['review'],
                    "rating": row['rating'],
                    "date_read": row['date_read']
                })
            return jsonify(books)
        finally:
            conn.close()
    except Exception as e:
        print(f"Error getting books: {e}")
        return jsonify({
            "status": "error",
            "message": f"책 목록을 가져오는 중 오류가 발생했습니다: {str(e)}"
        }), 500

# 책 수정
@app.route('/edit_book/<int:book_id>', methods=['POST'])
@login_required
def edit_book(book_id):
    try:
        data = request.json
        user_id = session['user_id']
        
        # 디버깅을 위한 로그 추가
        print(f"Received edit request for book {book_id}")
        print(f"Request data: {data}")
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 책이 존재하는지 먼저 확인
        cursor.execute("SELECT * FROM books WHERE id = ? AND user_id = ?", (book_id, user_id))
        book = cursor.fetchone()
        
        if not book:
            print(f"Book {book_id} not found or doesn't belong to user {user_id}")
            return jsonify({"error": "책을 찾을 수 없거나 권한이 없습니다."}), 404
            
        # 업데이트 쿼리 실행
        cursor.execute("""
            UPDATE books 
            SET title = ?, author = ?, rating = ?, review = ?
            WHERE id = ? AND user_id = ?
        """, (
            data.get('title'),
            data.get('author'),
            data.get('rating'),
            data.get('review', ''),
            book_id,
            user_id
        ))
        
        conn.commit()
        
        # 성공 로그
        print(f"Successfully updated book {book_id}")
        return jsonify({"success": True, "message": "책이 성공적으로 수정되었습니다."})
        
    except Exception as e:
        # 상세한 에러 로그
        print(f"Error editing book {book_id}: {str(e)}")
        return jsonify({"error": f"책 수정 중 오류가 발생했습니다: {str(e)}"}), 500
        
    finally:
        conn.close()

# 서버 시작
if __name__ == '__main__':
    init_db()  # 데이터베이스 초기화
    app.run(debug=True)