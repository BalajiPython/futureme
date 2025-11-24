document.addEventListener('DOMContentLoaded', async function () {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const letterForm = document.getElementById('letterForm');
    const lettersList = document.getElementById('lettersList');
    const deliveryDateSpan = document.getElementById('deliveryDate');
    const otpVerifyForm = document.getElementById('otpVerifyForm');

    // Check URL params for validation success
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('verified') === 'true' && document.referrer.includes('/verify')) {
        alert('Your email has been verified! You can now log in.');
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
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();
                
                if (response.ok) {
                    // Store email for OTP verification page
                    localStorage.setItem('pending_verification_email', email);
                    // Navigate to OTP verification page
                    window.location.href = '/verify-otp';
                } else {
                    alert(`Registration failed: ${data.detail || 'Please try again.'}`);
                }
            } catch (error) {
                alert('An error occurred during registration. Please try again.');
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

            try {
            const response = await fetch('/api/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                // No access_token returned, just redirect
                window.location.href = '/dashboard';
            } else {
                const errorData = await response.json();
                // Replace alert with inline error message display
                let errorMessage = errorData.detail || 'Please check your credentials.';
                displayLoginError(errorMessage);
            }
            } catch (error) {
                alert('An error occurred during login. Please try again.');
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
                    body: JSON.stringify({ 
                        title, 
                        content, 
                        delivery_date: deliveryDate.toISOString() 
                    })
                });

                console.log('Response status:', response.status);
                const responseBody = await response.text();
                console.log('Response body:', responseBody);

                if (response.ok) {
                    const data = JSON.parse(responseBody);
                    alert('Letter scheduled successfully.');
                    window.location.href = '/dashboard';
                } else {
                    try {
                        const errorData = JSON.parse(responseBody);
                        alert(`Failed to schedule letter: ${errorData.detail || 'Please try again.'}`);
                    } catch {
                        alert('Failed to schedule letter: Unknown error occurred.');
                    }
                    if (response.status === 401) {
                        localStorage.removeItem('access_token');
                        window.location.href = '/login?expired=true';
                    }
                }
            } catch (error) {
                alert('An error occurred. Please try again.');
                console.error('Letter creation error:', error);
            }
        });
    }

    // For confirmation page
    if (deliveryDateSpan) {
        const lastDeliveryDate = localStorage.getItem('last_delivery_date');
        if (lastDeliveryDate) {
            const formattedDate = new Date(lastDeliveryDate).toLocaleDateString(undefined, {
                year: 'numeric', 
                month: 'long', 
                day: 'numeric'
            });
            deliveryDateSpan.textContent = formattedDate;
            
            // Show letter title if available
            const letterTitle = localStorage.getItem('last_letter_title');
            if (letterTitle) {
                const titleElement = document.createElement('p');
                titleElement.className = 'letter-title';
                titleElement.innerHTML = `Your letter titled "<strong>${letterTitle}</strong>" will be delivered on that date.`;
                deliveryDateSpan.parentNode.insertBefore(titleElement, deliveryDateSpan.nextSibling);
            }
        } else {
            deliveryDateSpan.textContent = "the selected date";
        }
    }

    // Load letters for the dashboard
    if (lettersList) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            // Redirect to login if no token is available
            window.location.href = '/login?redirect=dashboard';
            return;
        }

        try {
            const response = await fetch('/api/letters', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const letters = await response.json();
                if (letters.length === 0) {
                    const emptyMessage = document.createElement('p');
                    emptyMessage.textContent = 'You have no scheduled letters yet. Write one now!';
                    emptyMessage.className = 'empty-message';
                    lettersList.parentNode.insertBefore(emptyMessage, lettersList);
                } else {
                    // Sort letters: pending first, then by delivery date
                    letters.sort((a, b) => {
                        // First sort by delivered status
                        if (a.is_delivered !== b.is_delivered) {
                            return a.is_delivered ? 1 : -1;
                        }
                        // Then sort by delivery date
                        return new Date(a.delivery_date) - new Date(b.delivery_date);
                    });
                    
                    letters.forEach(letter => {
                        const li = document.createElement('li');
                        li.className = 'letter-item';
                        
                        const deliveryDate = new Date(letter.delivery_date);
                        const isDelivered = letter.is_delivered;
                        const formattedDate = deliveryDate.toLocaleDateString(undefined, {
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric'
                        });
                        
                        // Calculate time remaining
                        let timeRemaining = '';
                        if (!isDelivered) {
                            const now = new Date();
                            const diffTime = Math.abs(deliveryDate - now);
                            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                            timeRemaining = diffDays === 1 ? 
                                'Delivers tomorrow!' : 
                                `${diffDays} days remaining`;
                        }
                        
                        li.innerHTML = `
                            <div class="letter-card ${isDelivered ? 'delivered' : ''}">
                                <h3>${letter.title}</h3>
                                <p class="delivery-date"><i class="fas fa-calendar-alt"></i> Delivery date: ${formattedDate}</p>
                                ${!isDelivered ? `<p class="time-remaining"><i class="fas fa-hourglass-half"></i> ${timeRemaining}</p>` : ''}
                                <p class="status ${isDelivered ? 'delivered' : 'pending'}">
                                    <i class="${isDelivered ? 'fas fa-check-circle' : 'fas fa-clock'}"></i>
                                    Status: ${isDelivered ? 'Delivered' : 'Pending'}
                                </p>
                            </div>
                        `;
                        
                        if (!isDelivered) {
                            const deleteBtn = document.createElement('button');
                            deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Delete';
                            deleteBtn.className = 'delete-btn';
                            deleteBtn.addEventListener('click', async () => {
                                if (confirm('Are you sure you want to delete this letter?')) {
                                    const deleted = await deleteLetter(letter.id, token);
                                    if (deleted) {
                                        li.remove();
                                        
                                        // Check if we need to show the empty message
                                        const remainingLetters = lettersList.querySelectorAll('li').length;
                                        if (remainingLetters === 0) {
                                            const emptyMessage = document.createElement('p');
                                            emptyMessage.textContent = 'You have no scheduled letters yet. Write one now!';
                                            emptyMessage.className = 'empty-message';
                                            lettersList.parentNode.insertBefore(emptyMessage, lettersList);
                                        }
                                    }
                                }
                            });
                            li.querySelector('.letter-card').appendChild(deleteBtn);
                        }
                        
                        lettersList.appendChild(li);
                    });
                }
            } else if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('access_token');
                window.location.href = '/login?expired=true&redirect=dashboard';
            } else {
                const errorData = await response.json();
                alert(`Failed to load letters: ${errorData.detail || 'Please try again.'}`);
            }
        } catch (error) {
            alert('An error occurred while loading your letters. Please try again.');
            console.error('Letter loading error:', error);
        }
    }
    
    // Function to delete a letter
    async function deleteLetter(letterId, token) {
        try {
            const response = await fetch(`/api/letters/${letterId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                return true;
            } else if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('access_token');
                window.location.href = '/login?expired=true';
                return false;
            } else {
                const errorData = await response.json();
                alert(`Failed to delete letter: ${errorData.detail || 'Please try again.'}`);
                return false;
            }
        } catch (error) {
            alert('An error occurred while deleting the letter. Please try again.');
            console.error('Letter deletion error:', error);
            return false;
        }
    }
    
    // Add logout functionality
    const logoutLink = document.querySelector('a[href="/logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('access_token');
            localStorage.removeItem('last_delivery_date');
            localStorage.removeItem('last_letter_title');
            window.location.href = '/login';
        });
    }
    
    // Check token on protected pages
    const protectedPages = ['/dashboard', '/write', '/confirmation'];
    const currentPath = window.location.pathname;
    
    if (protectedPages.includes(currentPath)) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = `/login?redirect=${currentPath.substring(1)}`;
        } else {
            // Verify token is valid
            try {
                const response = await fetch('/api/letters', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (!response.ok && response.status === 401) {
                    // Token expired or invalid
                    localStorage.removeItem('access_token');
                    window.location.href = `/login?expired=true&redirect=${currentPath.substring(1)}`;
                }
            } catch (error) {
                console.error('Token validation error:', error);
            }
        }
    }
    
    // Handle redirect after login
    if (currentPath === '/login') {
        const redirect = urlParams.get('redirect');
        if (redirect) {
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                const originalSubmit = loginForm.onsubmit;
                loginForm.onsubmit = async function(e) {
                    e.preventDefault();
                    const email = document.getElementById('email').value;
                    const password = document.getElementById('password').value;

                    try {
                        const response = await fetch('/api/token', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                            body: new URLSearchParams({ username: email, password })
                        });

                        if (response.ok) {
                            const data = await response.json();
                            localStorage.setItem('access_token', data.access_token);
                            window.location.href = `/${redirect}`;
                        } else {
                            const errorData = await response.json();
                            alert(`Login failed: ${errorData.detail || 'Please check your credentials.'}`);
                        }
                    } catch (error) {
                        alert('An error occurred during login. Please try again.');
                        console.error('Login error:', error);
                    }
                };
            }
        }
    }
    
    // Check for expired session message
    if (urlParams.get('expired') === 'true') {
        const message = document.createElement('div');
        message.className = 'flash-message flash-error';
        message.textContent = 'Your session has expired. Please log in again.';
        
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(message, main.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                message.remove();
            }, 5000);
        }
    }

    // Clear login error message on input change
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    if (emailInput && passwordInput) {
        emailInput.addEventListener('input', () => {
            const errorDiv = document.getElementById('loginError');
            if (errorDiv) errorDiv.textContent = '';
        });
        passwordInput.addEventListener('input', () => {
            const errorDiv = document.getElementById('loginError');
            if (errorDiv) errorDiv.textContent = '';
        });
    }
    
    // Add dark mode toggle
    const header = document.querySelector('header');
    if (header) {
        const darkModeToggle = document.createElement('button');
        darkModeToggle.className = 'dark-mode-toggle';
        darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        darkModeToggle.setAttribute('title', 'Toggle Dark Mode');
        header.appendChild(darkModeToggle);
        
        // Check for saved preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
        
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDark);
            this.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        });
    }
});
