class BookUI {
    static createBookElement(book) {
        const bookElement = document.createElement('div');
        bookElement.className = 'book-item';
        bookElement.innerHTML = `
            <div class="book-content">
                <h3>${book.title}</h3>
                <p class="author">${book.author}</p>
                <p class="rating">${'★'.repeat(book.rating)}${'☆'.repeat(5-book.rating)}</p>
            </div>
            <div class="book-actions">
                <button class="edit-btn" title="수정">🖋️</button>
                <button class="delete-btn" title="삭제">🗑️</button>
            </div>
        `;
        
        // 책 내용 클릭 시 상세 정보 표시
        const bookContent = bookElement.querySelector('.book-content');
        bookContent.addEventListener('click', () => {
            this.showBookDetail(book);
        });

        // 수정 버튼 클릭 이벤트
        const editBtn = bookElement.querySelector('.edit-btn');
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showEditForm(book);
        });

        // 삭제 버튼 클릭 이벤트
        const deleteBtn = bookElement.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm('정말로 이 책을 삭제하시겠습니까?')) {
                this.deleteBook(book.id);
            }
        });
        
        return bookElement;
    }

    static showBookDetail(book) {
        const modal = document.getElementById('bookModal');
        const modalContent = document.getElementById('modalContent');
        
        modalContent.innerHTML = `
            <div class="book-detail">
                <h2>${book.title}</h2>
                <p><strong>저자:</strong> ${book.author}</p>
                <p><strong>평점:</strong> ${'★'.repeat(book.rating)}${'☆'.repeat(5-book.rating)}</p>
                <p><strong>읽은 날짜:</strong> ${book.date_read}</p>
                <div class="review">
                    <strong>감상평:</strong>
                    <p>${book.review || '감상평이 없습니다.'}</p>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    static showEditForm(book) {
        const modal = document.getElementById('bookModal');
        const modalContent = document.getElementById('modalContent');
        
        modalContent.innerHTML = `
            <div class="edit-form">
                <h2>책 정보 수정</h2>
                <form id="editForm">
                    <input type="text" id="editTitle" value="${book.title}" required>
                    <input type="text" id="editAuthor" value="${book.author}" required>
                    <textarea id="editReview">${book.review || ''}</textarea>
                    <div class="rating">
                        <label>평점:</label>
                        <select id="editRating">
                            ${[5,4,3,2,1].map(num => 
                                `<option value="${num}" ${book.rating === num ? 'selected' : ''}>
                                    ${'★'.repeat(num)}${'☆'.repeat(5-num)}
                                </option>`
                            ).join('')}
                        </select>
                    </div>
                    <input type="date" id="editDateRead" value="${book.date_read}" required>
                    <button type="submit" class="save-btn">저장하기</button>
                </form>
            </div>
        `;

        const editForm = modalContent.querySelector('#editForm');
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const updatedData = {
                id: book.id,
                title: document.getElementById('editTitle').value,
                author: document.getElementById('editAuthor').value,
                review: document.getElementById('editReview').value,
                rating: document.getElementById('editRating').value,
                date_read: document.getElementById('editDateRead').value
            };

            try {
                const response = await fetch(`/update_book/${book.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(updatedData)
                });

                const result = await response.json();
                if (result.status === 'success') {
                    this.showMessage('책 정보가 수정되었습니다.');
                    modal.style.display = 'none';
                    window.dispatchEvent(new Event('booksUpdated'));
                } else {
                    this.showMessage('수정 중 오류가 발생했습니다.', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showMessage('수정 중 오류가 발생했습니다.', 'error');
            }
        });
        
        modal.style.display = 'block';
    }

    static async deleteBook(bookId) {
        try {
            const response = await fetch(`/delete_book/${bookId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            if (result.status === 'success') {
                this.showMessage('책이 삭제되었습니다.');
                window.dispatchEvent(new Event('booksUpdated'));
            } else {
                this.showMessage('삭제 중 오류가 발생했습니다.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showMessage('삭제 중 오류가 발생했습니다.', 'error');
        }
    }

    static clearForm() {
        document.getElementById('bookForm').reset();
    }

    static showMessage(message, type = 'success') {
        // 기존 메시지가 있다면 제거
        const existingMessage = document.querySelector('.alert');
        if (existingMessage) {
            existingMessage.remove();
        }

        // 새 메시지 생성
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type}`;
        messageDiv.textContent = message;
        
        // 메시지를 추가할 위치 찾기
        const addBookForm = document.querySelector('.add-book-form');
        if (addBookForm) {
            // add-book-form의 시작 부분에 메시지 삽입
            addBookForm.insertAdjacentElement('afterbegin', messageDiv);
        }

        // 3초 후 메시지 제거
        setTimeout(() => messageDiv.remove(), 3000);
    }
}

// 모달 닫기 기능
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('bookModal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = () => {
        modal.style.display = 'none';
    };
    
    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    // booksUpdated 이벤트 리스너 추가
    window.addEventListener('booksUpdated', () => {
        // BookManager의 loadBooks 메서드를 호출하기 위해 새로운 인스턴스 생성
        new BookManager().loadBooks();
    });
});