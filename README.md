# PAMANGKOT Inquiry Management System

A Flask-based web application for managing customer inquiries with role-based login, search, filtering, and pagination. Built with SQLite and Bootstrap 5.

## Features

- **User Authentication**: Login with credentials (admin/admin123, user/user123)
- **Inquiry Management**: Submit, view, edit, and delete inquiries
- **Search & Filter**: Search by name, email, or inquiry text
- **Pagination**: Configurable page size (5, 10, 25 items)
- **Responsive Design**: Mobile-friendly Bootstrap 5 UI
- **Modal Preview**: View full inquiry details in a popup

## Quick Start

### Prerequisites
- Python 3.8+
- pip and virtualenv (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd pythonflask
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example env file
   cp .env.example .env

   # Edit .env and set your SECRET_KEY (optional for development)
   # For production, use a strong random key
   ```

5. **Run the app**
   ```bash
   python capstone.py
   ```

   Or using Flask CLI:
   ```bash
   flask --app capstone run
   ```

   The app will be available at `http://localhost:5001`

### Default Credentials

- **Admin**: username `admin`, password `admin123`
- **User**: username `user`, password `user123`

> ⚠️ Change these credentials in production!

## Project Structure

```
.
├── capstone.py                 # Main Flask app with routes and database functions
├── seed_db.py                  # Database seeding script (if needed)
├── templates/
│   ├── base.html              # Base template with navbar, footer, styling
│   ├── dashboard.html         # Main inquiry dashboard (protected)
│   ├── inquiry-form.html      # Inquiry submission form
│   ├── login.html             # Login page
│   ├── landing.html           # Landing page
│   ├── about.html             # About page
│   ├── success.html           # Success feedback
│   └── failed.html            # Error feedback
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
└── README.md                  # This file
```

## Database

The app uses **SQLite** with two tables:

### `inquiry` table
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT)
- `email` (TEXT)
- `inquiry` (TEXT)

### `users` table
- `id` (INTEGER PRIMARY KEY)
- `username` (TEXT UNIQUE)
- `password` (TEXT) — hashed with Werkzeug

The database file `database.db` is created automatically on first run.

## API Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Landing page or dashboard (if logged in) |
| `/login` | GET/POST | No | User login |
| `/logout` | GET | Yes | User logout |
| `/about` | GET | No | About page |
| `/inquiry` | GET/POST | No | Submit new inquiry |
| `/dashboard` | GET | Yes | View all inquiries (paginated, searchable) |
| `/inquiry/<id>/edit` | GET | Yes | Edit inquiry form |
| `/update/<id>` | POST | Yes | Update inquiry |
| `/delete/<id>` | POST | Yes | Delete inquiry |

## Development

### Running with Waitress (Windows local testing)
```bash
pip install waitress
waitress-serve --listen=0.0.0.0:8000 capstone:app
```

### Running with Gunicorn (Linux/Mac)
```bash
gunicorn capstone:app
```

## Deployment

### Deploy to Render

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <github-repo-url>
   git push -u origin main
   ```

2. **Create Render Service**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn capstone:app`
     - **Environment**: Select "Python 3"

3. **Set Environment Variables** in Render dashboard:
   ```
   SECRET_KEY=<generate-strong-random-key>
   FLASK_ENV=production
   DEBUG=False
   ```

4. **Database Persistence** (Important!)
   - **Option A**: Use Render Postgres (recommended for production)
     - Add PostgreSQL instance in Render
     - Update connection string in env
     - Migrate codebase to use SQLAlchemy/psycopg2
   
   - **Option B**: Use Render Persistent Disk
     - Paid add-on; stores `database.db` across deploys
   
   - **Option C**: Accept ephemeral storage
     - Data lost on redeploy; OK for testing only

5. **Deploy**
   - Render auto-deploys on push to main
   - Check logs for errors

### Environment Variables for Production

Set these in Render (or your hosting provider):

```
SECRET_KEY=<strong-random-key-from-secrets-generator>
FLASK_ENV=production
DEBUG=False
DATABASE_URL=<postgres-or-sqlite-url-if-using-custom-db>
```

## Security Notes

⚠️ **Before deploying to production:**
- Change `SECRET_KEY` to a strong random value
- Update default user credentials (`admin123`, `user123`)
- Implement email verification for inquiries
- Add rate limiting to login endpoint
- Use HTTPS (Render provides free SSL)
- Consider adding CSRF protection

## Future Improvements

- [ ] Integrate SQLAlchemy ORM
- [ ] Add email notifications
- [ ] Add inquiry status tracking (New, In Progress, Resolved)
- [ ] Export inquiries to CSV/PDF
- [ ] Admin dashboard with statistics
- [ ] Soft delete (archive) instead of permanent delete
- [ ] Audit logging
- [ ] Unit tests with pytest

## Support

For issues or questions, check the code comments in `capstone.py` or open an issue on GitHub.

---

**Version**: 1.0.0  
**Last Updated**: February 2026
