// Letter management functionality
class LetterManager {
    static async fetchLetters() {
        const response = await fetch('/api/letters/');
        if (!response.ok) throw new Error('Failed to fetch letters');
        return await response.json();
    }

    static async deleteLetter(id) {
        const response = await fetch(`/api/letters/${id}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        return response.ok;
    }

    static formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}

class EmailService {
    static async sendVerification(email) {
        const response = await fetch('/api/send-verification', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ email })
        });
        return response.ok;
    }
}

class LetterScheduler {
    static validateDeliveryDate(date) {
        const deliveryDate = new Date(date);
        const now = new Date();
        return deliveryDate > now;
    }

    static async scheduleLetter(letterData) {
        if (!this.validateDeliveryDate(letterData.delivery_date)) {
            throw new Error('Delivery date must be in the future');
        }

        const response = await fetch('/api/letters/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(letterData)
        });

        if (!response.ok) throw new Error('Failed to schedule letter');
        return response.json();
    }
}

// Initialize features based on current page
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    
    if (currentPath === '/dashboard') {
        LetterManager.fetchLetters()
            .then(data => {
                // Update dashboard UI
                const lettersList = document.getElementById('lettersList');
                if (!lettersList) return;
                // ... letter rendering logic ...
            })
            .catch(console.error);
    }
    
    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });
    }
});
