# FutureMe - Write Letters to Your Future Self

FutureMe is a web application that allows users to write letters to their future selves and receive them at a specified date. It's a personal time capsule service that helps users track their personal growth and reflect on their journey.

## Features

- Write letters to your future self
- Set custom delivery dates
- Track letter status
- Secure user authentication
- Email notifications
- Responsive design
- Dark mode support

## Tech Stack

- Django
- Python
- HTML/CSS
- JavaScript
- SQLite (Development)
- PostgreSQL (Production)
- APScheduler for letter delivery

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/futureme.git
cd futureme
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file with the following variables:

```
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django Documentation
- Bootstrap
- Font Awesome
- Google Fonts 