document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    
    // 실시간 유효성 검사
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const submitButton = document.querySelector('button[type="submit"]');

    function updateSubmitButton() {
        // 아이디: 4-20자의 영문자와 숫자
        const isUsernameValid = /^[a-zA-Z0-9]{4,20}$/.test(username.value);
        // 비밀번호: 4-20자
        const isPasswordValid = password.value.length >= 4 && password.value.length <= 20;
        // 비밀번호 확인: 일치 여부
        const isPasswordMatch = password.value === confirmPassword.value;

        // 모든 조건이 충족되면 버튼 활성화
        submitButton.disabled = !(isUsernameValid && isPasswordValid && isPasswordMatch);
    }

    function validateUsername(value) {
        const regex = /^[a-zA-Z0-9]{4,20}$/;
        const message = document.getElementById('usernameMessage');
        
        if (!regex.test(value)) {
            message.textContent = '아이디는 4-20자의 영문자와 숫자만 사용 가능합니다.';
            message.className = 'validation-message error';
            return false;
        }
        message.textContent = '사용 가능한 아이디입니다.';
        message.className = 'validation-message success';
        return true;
    }

    function validatePassword(value) {
        const message = document.getElementById('passwordMessage');
        
        if (value.length < 4 || value.length > 20) {
            message.textContent = '비밀번호는 4-20자 사이여야 합니다.';
            message.className = 'validation-message error';
            return false;
        }
        message.textContent = '사용 가능한 비밀번호입니다.';
        message.className = 'validation-message success';
        return true;
    }

    function validateConfirmPassword() {
        const message = document.getElementById('confirmPasswordMessage');
        
        if (password.value !== confirmPassword.value) {
            message.textContent = '비밀번호가 일치하지 않습니다.';
            message.className = 'validation-message error';
            return false;
        }
        message.textContent = '비밀번호가 일치합니다.';
        message.className = 'validation-message success';
        return true;
    }

    username.addEventListener('input', () => {
        validateUsername(username.value);
        updateSubmitButton();
    });

    password.addEventListener('input', () => {
        validatePassword(password.value);
        if (confirmPassword.value) validateConfirmPassword();
        updateSubmitButton();
    });

    confirmPassword.addEventListener('input', () => {
        validateConfirmPassword();
        updateSubmitButton();
    });

    // 회원가입 폼 제출 부분만 수정
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        username: username.value,
        password: password.value
    };

    console.log('Attempting to register with:', formData.username);  // 로그 추가

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        console.log('Server response:', data);  // 서버 응답 로그
        
        if (response.ok) {
            alert(data.message);
            window.location.href = '/login';
        } else {
            // 더 자세한 에러 메시지 표시
            const errorMessage = data.message || '회원가입 중 오류가 발생했습니다.';
            alert(errorMessage);
            console.error('Registration failed:', errorMessage);
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('서버와의 통신 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
    });
});