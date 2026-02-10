# Deploy to Render - Step-by-Step Guide

## Pre-Deploy Checklist

✅ Your app is **Render-compatible**:
- Has `Procfile` with: `web: gunicorn capstone:app`
- Has `requirements.txt` with gunicorn and dependencies
- Environment variables configured (.env support)
- Port automatically reads from Render's PORT env var
- Passwords hashed with Werkzeug
- Not hardcoded secrets

⚠️ **Known limitation**: SQLite database is **ephemeral** (data lost on redeploy)
- Data persists during normal uptime
- Resets when Render redeploys your code
- OK for demos; for production, add Postgres (free tier available)

---

## Step 1: Push Code to GitHub

1. **Initialize git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Flask inquiry system"
   ```

2. **Add GitHub remote and push**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/pythonflask.git
   git branch -M main
   git push -u origin main
   ```

3. **Verify** your repo is on GitHub with these files:
   - `capstone.py`
   - `requirements.txt`
   - `Procfile`
   - `.env.example` (NOT `.env` — that's local only)
   - `templates/` folder
   - `.env` should be in `.gitignore` (don't commit it)

---

## Step 2: Create `.gitignore`

Create a `.gitignore` file in your repo root:

```
# Environment
.env
.venv
venv/

# Database
database.db
*.db

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.Python

# IDE
.vscode/
.idea/
*.swp
```

Commit and push:
```bash
git add .gitignore
git commit -m "Add gitignore"
git push
```

---

## Step 3: Create Render Service

1. **Go to [render.com](https://render.com)** and sign up (free)

2. **Click "New +" → "Web Service"**

3. **Connect GitHub**:
   - Click "Connect Account" (or use existing GitHub account)
   - Select your `pythonflask` repository
   - Click "Connect"

4. **Configure the Web Service**:
   - **Name**: `inquiry-system` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn capstone:app`
   - **Instance Type**: `Free` (for testing)

5. **Click "Create Web Service"** and wait for build to complete (2-3 min)

---

## Step 4: Set Environment Variables

1. In Render dashboard, go to your service → **Environment**

2. **Add these variables**:

   | Key | Value | Note |
   |-----|-------|------|
   | `SECRET_KEY` | `[generate-strong-random-key]` | See below |
   | `FLASK_ENV` | `production` | **Important!** |
   | `DEBUG` | `False` | **Important!** |

3. **Generate a strong SECRET_KEY**:
   Option A (Python):
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```
   Option B: Use [this generator](https://randomkeygen.com/)
   
   Copy the output and paste into Render's `SECRET_KEY` field.

4. **Save** environment variables

---

## Step 5: Verify Deployment

1. **Check Render logs**:
   - Go to your service → **Logs**
   - Look for: `Listening on 0.0.0.0:10000` (port varies)
   - If red errors, scroll up to diagnose

2. **Visit your app**:
   - Click the URL at the top of your Render dashboard (e.g., `https://inquiry-system.onrender.com`)
   - Should see the login page

3. **Test login**:
   - Username: `admin`
   - Password: `admin123`
   - (Or user/user123)

4. **Test a submission**:
   - Go to `/inquiry`
   - Submit an inquiry
   - View it in the dashboard

---

## Step 6: Auto-Deploy on Push

Your app now **auto-deploys** when you push to `main`:

```bash
# Make a change
echo "# Updated" >> README.md

# Commit and push
git add .
git commit -m "Update readme"
git push origin main
```

Render will automatically rebuild and redeploy within 1-2 minutes. Check **Logs** to monitor.

---

## Troubleshooting

### Build fails: "No module named X"

**Problem**: Package is missing from `requirements.txt`

**Fix**:
```bash
pip freeze | grep -i <package-name>
```

Then add to `requirements.txt` and push:
```bash
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

### App crashes after deploy

**Check logs**:
1. Go to Render dashboard → **Logs**
2. Look for error messages
3. Common issues:
   - Missing env var (check "Environment" tab)
   - Typo in `Procfile` or `capstone.py`
   - Database permission issue

### "Cannot connect to database" or "No data"

**Expected** on Render — SQLite is ephemeral. Data resets on redeploy.

**Solution**:
- For production: Add Render PostgreSQL (instructions below)
- For testing: This is OK; just aware data won't persist across deploys

---

## Optional: Add PostgreSQL (Persistent Database)

If you want data to persist across deploys:

1. **Create Postgres instance** in Render:
   - Dashboard → "New +" → "PostgreSQL"
   - Name: `inquiry-db` (or your choice)
   - Click "Create Database"

2. **Copy the connection string** from the Postgres instance page

3. **Add to your Web Service environment**:
   - Key: `DATABASE_URL`
   - Value: `[paste connection string]`

4. **Update `capstone.py`** to use PostgreSQL (requires code change; ask if needed)

---

## Cost & Limits (Free Tier)

| Resource | Free Tier | Limit |
|----------|-----------|-------|
| **Web Service** | 750 hours/month | ~31 hours/day |
| **PostgreSQL** | 100 MB storage | Ephemeral after 30 days |
| **Bandwidth** | Unlimited | Fair use |
| **Spins down** | After 15 min inactivity | Rebuilds on request (50s) |

---

## Next Steps

- ✅ App deployed on Render
- 📊 Add PostgreSQL for persistent data (optional)
- 🔒 Change default admin credentials in production
- 📧 Add email notifications (feature)
- 📝 Monitor logs for errors
- 🚀 Set up CI/CD pipeline (optional)

---

## Quick Reference

**Your app URL**: `https://your-app-name.onrender.com`

**Render Dashboard**: [render.com/dashboard](https://render.com/dashboard)

**View Logs**: Service → Logs

**Environment Variables**: Service → Environment

**Redeploy manually**: Service → "Deploy" button

---

## Support

If something breaks:
1. Check Render **Logs** tab first
2. Verify all **Environment** variables are set
3. Ensure `requirements.txt` has all dependencies
4. Check `Procfile` syntax: `web: gunicorn capstone:app`

Good luck! 🚀
