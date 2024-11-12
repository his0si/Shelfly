class BookManager {
    constructor() {
        this.bookForm = document.getElementById('bookForm');
        this.booksList = document.getElementById('booksList');
        this.isSubmitting = false; // 제출 상태 추적
        this.initialize();
    }

    initialize() {
        this.loadBooks();
        this.setupEventListeners();
        console.log('BookManager initialized');
    }

    setupEventListeners() {
        this.bookForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!this.isSubmitting) {  // 제출 중이 아닐 때만 처리
                this.handleBookSubmit(e);
            }
        });

        // 추가하기 버튼에 대한 직접적인 이벤트 리스너
        const submitBtn = document.querySelector('.submit-btn');
        if (submitBtn) {
            submitBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (!this.isSubmitting) {  // 제출 중이 아닐 때만 처리
                    this.handleBookSubmit(e);
                }
            });
        }

        // booksUpdated 이벤트 리스너
        window.addEventListener('booksUpdated', () => {
            this.loadBooks();
        });
    }

    async handleBookSubmit(e) {
        e.preventDefault();
        
        if (this.isSubmitting) {
            console.log('Already submitting...');
            return;
        }

        const submitBtn = document.querySelector('.submit-btn');
        
        try {
            this.isSubmitting = true;  // 제출 시작
            submitBtn.disabled = true;  // 버튼 비활성화
            submitBtn.style.backgroundColor = '#cccccc';  // 버튼 스타일 변경
            submitBtn.textContent = '추가 중...';  // 버튼 텍스트 변경
            
            const bookData = {
                title: document.getElementById('title').value.trim(),
                author: document.getElementById('author').value.trim(),
                review: document.getElementById('review').value,
                rating: document.getElementById('rating').value,
                date_read: document.getElementById('dateRead').value
            };

            // 기본적인 유효성 검사
            if (!bookData.title || !bookData.author) {
                BookUI.showMessage('제목과 저자를 입력해주세요.', 'error');
                return;
            }

            console.log('Sending book data:', bookData);

            const response = await fetch('/add_book', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bookData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if(data.status === 'success') {
                    BookUI.showMessage('책이 성공적으로 추가되었습니다!');
                    BookUI.clearForm();
                    this.loadBooks();
                } else {
                    BookUI.showMessage(data.message || '책 추가 실패', 'error');
                }
            } else {
                BookUI.showMessage(data.message || '책 추가 실패', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            BookUI.showMessage('책 추가 중 오류가 발생했습니다.', 'error');
        } finally {
            // 작업 완료 후 상태 복원
            this.isSubmitting = false;
            submitBtn.disabled = false;
            submitBtn.style.backgroundColor = '#4CAF50';
            submitBtn.textContent = '추가하기';
        }
    }

    async loadBooks() {
        try {
            const response = await fetch('/get_books');
            const books = await response.json();
            console.log('Loaded books:', books);
            
            this.booksList.innerHTML = '';
            if (books.length === 0) {
                this.booksList.innerHTML = '<p class="no-books">저장된 책이 없습니다.</p>';
                return;
            }
            
            books.forEach(book => {
                const bookElement = BookUI.createBookElement(book);
                this.booksList.appendChild(bookElement);
            });
        } catch (error) {
            console.error('Error loading books:', error);
            BookUI.showMessage('책 목록을 불러오는 중 오류가 발생했습니다.', 'error');
        }
    }
}

// DOM이 로드되면 BookManager 인스턴스 생성
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded');
    new BookManager();
});