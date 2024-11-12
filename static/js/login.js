document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                alert(data.message);
                window.location.href = '/';  // 메인 페이지로 리다이렉트
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('로그인 중 오류가 발생했습니다.');
        }
    });
});