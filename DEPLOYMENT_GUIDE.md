# 🚀 ExtemporeAI Deployment & Upload Guide

This guide explains how to upload and publish the **ExtemporeAI** web application to the internet so anyone can use it.

---

## 📋 Pre-Flight Checklist
- [x] **Git Repository Initialized**: Pre-configured with `.gitignore` and committed on branch `main`.
- [x] **Vercel Config**: `vercel.json` configured with `@vercel/python` serverless router.
- [x] **Dual Database Layer**: Works with Cloud MySQL (Aiven, TiDB, Railway) or automatic `/tmp` SQLite mirror on serverless lambdas.
- [x] **Favicon Assets**: High-resolution vector SVG and ICO favicons in `static/`.

---

## 🌟 Method 1: Deploy to Vercel via GitHub (Recommended)

Vercel provides free, instant HTTPS hosting with automatic CI/CD whenever you push updates.

### Step 1: Create a GitHub Repository
1. Log into your [GitHub account](https://github.com/).
2. Click **New Repository** (or visit https://github.com/new).
3. Name the repository: `extempore-ai`.
4. Choose **Public** (or **Private**) and **DO NOT** check "Add README" (we already have one).
5. Click **Create repository**.

### Step 2: Push your Code to GitHub
Open PowerShell or Terminal in this project directory:
```powershell
cd C:\Users\AMAN\.gemini\antigravity\scratch\ai_extempore_app

# Link your new GitHub repository (replace with your username)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/extempore-ai.git

# Push code to main branch
git push -u origin main
```

---

### Step 3: Import Project in Vercel
1. Log into [Vercel](https://vercel.com/) (sign in with your GitHub account).
2. On your Vercel Dashboard, click **"Add New..."** > **"Project"**.
3. Under *Import Git Repository*, locate `extempore-ai` and click **Import**.
4. In the Project Configuration:
   - **Framework Preset**: Leave as *Other*.
   - **Root Directory**: Leave as `./` (default).
5. Click **Environment Variables** (expand section) and add:
   | Key | Example Value | Description |
   | :--- | :--- | :--- |
   | `SECRET_KEY` | `super-secret-key-aman-2026` | Session encryption key |
   | `ALLOW_SQLITE_FALLBACK` | `true` | Enables serverless database fallback |
   | `GEMINI_API_KEY` | `AIzaSy...` | *(Optional)* Google AI Studio key for LLM grading |
6. Click **Deploy**! 🚀
7. In ~60 seconds, your site is live at: `https://extempore-ai.vercel.app` (or your chosen custom domain).

---

## 🗄️ Setting Up Free Cloud MySQL for Vercel

> **Why is this needed?**
> When your app is published on Vercel, it runs on cloud serverless servers. It cannot connect to `localhost:3306` running on your personal computer.

### Option A: TiDB Serverless (100% Free Forever)
1. Go to [TiDB Cloud](https://tidbcloud.com/) and create a free account.
2. Click **Create Cluster** > Select **Serverless (Free)**.
3. Once active, click **Connect** > choose **Python (PyMySQL)**.
4. Copy the connection parameters and add them to your Vercel Environment Variables:
   - `DB_HOST`
   - `DB_PORT` (`4000`)
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME` (`test` or `extempore_db`)

### Option B: Aiven for MySQL (Free Tier)
1. Go to [Aiven.io](https://aiven.io/) and create a free MySQL database in your preferred cloud region.
2. Enter the host, user, and password into Vercel settings or the app's in-browser **Database Settings** modal.

---

## 💻 Method 2: Deploy directly via Vercel CLI

If you prefer deploying straight from your terminal without opening GitHub:
```powershell
# 1. Install Vercel CLI (Node.js required)
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy to production
cd C:\Users\AMAN\.gemini\antigravity\scratch\ai_extempore_app
vercel --prod
```

---

## 🎨 Favicon & Branding
The app includes:
- **SVG Favicon**: `/static/favicon.svg` (Sharp on Retina / 4K displays).
- **ICO Favicon**: `/static/favicon.ico` (Standard fallback for all browsers).
- **Root Route**: `/favicon.ico` automatically routed to static favicon in Flask.
