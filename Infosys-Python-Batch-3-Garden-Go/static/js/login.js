function toggleSecretKeyField() {
    const roleSelect = document.getElementById('role');
    const secretKeyField = document.getElementById('secret-key-group');
    if (roleSelect.value === 'admin') {
        secretKeyField.classList.remove('hidden');
    } else {
        secretKeyField.classList.add('hidden');
    }
}
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggle-password');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.textContent = '🔒';
    } else {
        passwordInput.type = 'password';
        toggleIcon.textContent = '👁️';
    }
}
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim());
}

function validatePassword(password) {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password.trim());
}

function validateMobileNumber(mobile) {
    const mobileRegex = /^[0-9]{10}$/;
    return mobileRegex.test(mobile.trim());
}

function validateAdminKey(role, secretKey) {
    return !(role === 'admin' && secretKey.trim() === '');
}

function showErrorMessage(element, message) {
    element.textContent = message;
}

function clearErrorMessage(element) {
    element.textContent = '';
}

function validatesignupForm(event) {
    event.preventDefault();
    let isValid = true;

    // Email validation
    const email = document.getElementById('email');
    const emailError = document.getElementById('email-error');
    if (!validateEmail(email.value)) {
        showErrorMessage(emailError, 'Enter a valid email address.');
        isValid = false;
    } else {
        clearErrorMessage(emailError);
    }

    // Password validation
    const password = document.getElementById('password');
    const passwordError = document.getElementById('password-error');
    if (!validatePassword(password.value)) {
        showErrorMessage(passwordError, 'Password must include at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.');
        isValid = false;
    } else {
        clearErrorMessage(passwordError);
    }

    // Mobile number validation
    const mobile = document.getElementById('mobile');
    const mobileError = document.getElementById('mobile-error');
    if (!validateMobileNumber(mobile.value)) {
        showErrorMessage(mobileError, 'Enter a valid 10-digit mobile number.');
        isValid = false;
    } else {
        clearErrorMessage(mobileError);
    }

    // Secret Key validation for admin role
    const role = document.getElementById('role');
    const secretKey = document.getElementById('admin-key');
    const secretKeyError = document.getElementById('secret-key-error');
    if (!validateAdminKey(role.value, secretKey.value)) {
        showErrorMessage(secretKeyError, 'Secret key is required for admin.');
        isValid = false;
    } else {
        clearErrorMessage(secretKeyError);
    }

    if (isValid) {
        document.querySelector('.signup-form').submit();
    }
}

function validateloginForm(event) {
    event.preventDefault();
    let isValid = true;

    // Email validation
    const email = document.getElementById('email');
    const emailError = document.getElementById('email-error');
    if (!validateEmail(email.value)) {
        showErrorMessage(emailError, 'Enter a valid email address.');
        isValid = false;
    } else {
        clearErrorMessage(emailError);
    }

    // Password validation
    const password = document.getElementById('password');
    const passwordError = document.getElementById('password-error');
    if (!validatePassword(password.value)) {
        showErrorMessage(passwordError, 'Password must include at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.');
        isValid = false;
    } else {
        clearErrorMessage(passwordError);
    }

    if (isValid) {
        document.querySelector('.signup-form').submit();
    }
}

function validatenewpassword(event) {
    event.preventDefault();
    let isValid = true;

    const password = document.getElementById('password');
    const passwordError = document.getElementById('password-error');
    if (!validatePassword(password.value)) {
        showErrorMessage(passwordError, 'Password must include at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.');
        isValid = false;
    } else {
        clearErrorMessage(passwordError);
    }

    if (isValid) {
        document.querySelector('.signup-form').submit();
    }
}
