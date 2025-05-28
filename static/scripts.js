// Check URL params for validation success
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('verified') === 'true' && document.referrer.includes('/verify')) {
    alert('Your email has been verified! You can now log in.');
    // Add a redirect to the login page after verification
    setTimeout(() => {
        window.location.href = '/login';
    }, 2000);
}

// Handle OTP verification
if (otpVerifyForm) {
    // Prefill email field if available from localStorage
    const pendingEmail = localStorage.getItem('pending_verification_email');
    const emailField = document.getElementById('email');
    if (pendingEmail && emailField) {
        emailField.value = pendingEmail;
    }

    otpVerifyForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const otpCode = document.getElementById('otp_code').value;

        try {
            const response = await fetch('/api/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, otp_code: otpCode })
            });

            const data = await response.json();
            
            if (response.ok) {
                localStorage.removeItem('pending_verification_email');
                alert('Email verified successfully! Please log in.');
                window.location.href = '/login?verified=true';
            } else {
                alert(`Verification failed: ${data.detail || 'Please try again.'}`);
            }
        } catch (error) {
            alert('An error occurred during verification. Please try again.');
            console.error('Verification error:', error);
        }
    });
}

// Handle registration
if (registerForm) {
    registerForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password1 = document.getElementById('password1').value;
        const password2 = document.getElementById('password2').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ email, password1, password2 })
            });

            const data = await response.json();
            
            if (response.ok) {
                // Store email for OTP verification page
                localStorage.setItem('pending_verification_email', email);
                // Navigate to OTP verification page with email parameter
                window.location.href = `/verify-otp?email=${encodeURIComponent(email)}`;
            } else {
                const errorDiv = document.getElementById('registerError');
                errorDiv.textContent = data.detail || 'Registration failed. Please try again.';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            const errorDiv = document.getElementById('registerError');
            errorDiv.textContent = 'An error occurred during registration. Please try again.';
            errorDiv.style.display = 'block';
            console.error('Registration error:', error);
        }
    });
}

// Handle login
if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                window.location.href = '/dashboard';
            } else {
                const data = await response.json();
                const errorDiv = document.getElementById('loginError');
                errorDiv.textContent = data.detail || 'Invalid credentials. Please try again.';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            const errorDiv = document.getElementById('loginError');
            errorDiv.textContent = 'An error occurred during login. Please try again.';
            errorDiv.style.display = 'block';
            console.error('Login error:', error);
        }
    });
}

// Function to display login errors inline
function displayLoginError(message) {
    let errorDiv = document.getElementById('loginError');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'loginError';
        errorDiv.className = 'error-message';
        const loginForm = document.getElementById('loginForm');
        loginForm.parentNode.insertBefore(errorDiv, loginForm.nextSibling);
    }
    errorDiv.textContent = message;
}

// Handle letter creation
if (letterForm) {
    // Set minimum date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minDate = tomorrow.toISOString().split('T')[0];
    document.getElementById('delivery_date').min = minDate;

    // Add basic formatting toolbar
    const contentArea = document.getElementById('content');
    if (contentArea) {
        const toolbar = document.createElement('div');
        toolbar.className = 'formatting-toolbar';
        toolbar.innerHTML = `
            <button type="button" data-format="bold" title="Bold"><i class="fas fa-bold"></i></button>
            <button type="button" data-format="italic" title="Italic"><i class="fas fa-italic"></i></button>
            <button type="button" data-format="underline" title="Underline"><i class="fas fa-underline"></i></button>
            <button type="button" data-format="list" title="Bullet List"><i class="fas fa-list-ul"></i></button>
            <button type="button" data-format="numbered" title="Numbered List"><i class="fas fa-list-ol"></i></button>
        `;
        contentArea.parentNode.insertBefore(toolbar, contentArea);
        
        // Set up formatting buttons
        toolbar.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', function() {
                const format = this.getAttribute('data-format');
                const textarea = document.getElementById('content');
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const selectedText = textarea.value.substring(start, end);
                let formattedText = '';
                
                switch(format) {
                    case 'bold':
                        formattedText = `<strong>${selectedText}</strong>`;
                        break;
                    case 'italic':
                        formattedText = `<em>${selectedText}</em>`;
                        break;
                    case 'underline':
                        formattedText = `<u>${selectedText}</u>`;
                        break;
                    case 'list':
                        formattedText = `\n<ul>\n  <li>${selectedText}</li>\n</ul>\n`;
                        break;
                    case 'numbered':
                        formattedText = `\n<ol>\n  <li>${selectedText}</li>\n</ol>\n`;
                        break;
                }
                
                textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
                textarea.focus();
                textarea.setSelectionRange(start + formattedText.length, start + formattedText.length);
            });
        });
    }

    letterForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const title = document.getElementById('title').value;
        const content = document.getElementById('content').value;
        const deliveryDateInput = document.getElementById('delivery_date').value;
        
        // Convert the delivery date to ISO format for API
        const deliveryDate = new Date(`${deliveryDateInput}T12:00:00`);
        
        // Validate future date
        if (deliveryDate <= new Date()) {
            alert('Delivery date must be in the future.');
            return;
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('You need to be logged in to create a letter.');
            window.location.href = '/login';
            return;
        }

        try {
            const response = await fetch('/api/letters', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ title, content, delivery_date: deliveryDate })
            });

            if (response.ok) {
                alert('Letter created successfully!');
                window.location.href = '/dashboard';
            } else {
                const data = await response.json();
                const errorDiv = document.getElementById('letterError');
                errorDiv.textContent = data.detail || 'An error occurred while creating the letter. Please try again.';
                errorDiv.style.display = 'block';
            }
        } catch (error) {
            const errorDiv = document.getElementById('letterError');
            errorDiv.textContent = 'An error occurred during letter creation. Please try again.';
            errorDiv.style.display = 'block';
            console.error('Letter creation error:', error);
        }
    });
}