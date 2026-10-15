# AI-Powered Extempore & Current Affairs Practice App

**Personal / Portfolio Project**  
**Author:** Aman (Cybersecurity Student)  
**Target:** UPSC / State PSC Aspirants, Debate Competitors, Journalism & Media Students

---

## 🌟 Features Built

1. **Live News Feed & Headline Ticker**:
   - Pulls real-time headlines across 6 categories: *National & Polity (UPSC)*, *International Relations*, *Tech & Cybersecurity*, *Economy*, *Sports & Society*, and *Live Mix*.
   - Uses zero-configuration Google News RSS + fallback news feeds.
2. **AI Extempore Question Generator**:
   - Transforms live breaking headlines into analytical, thought-provoking questions requiring depth and multi-dimensional analysis.
   - Built-in Gemini API support + smart local editorial framing templates.
3. **Timed Brainstorming & Preparation Arena (30–60 Seconds)**:
   - Animated SVG circular countdown timer with color shifting (Green ➔ Amber ➔ Red).
   - 3-point rapid scratchpad (*1. Opening Thesis, 2. Key Arguments, 3. Way Forward*).
   - Audio warning chime when 5 seconds remain.
4. **Live Answer Arena (5-Minute Window)**:
   - Distraction-free focus view with pinned question prompt.
   - Live digital timer with urgency styling.
   - Pacing Guide bar showing recommended stage allocation:
     - Stage 1: Context & Stance (0 - 1m)
     - Stage 2: Core Analysis & Dimensions (1m - 3.5m)
     - Stage 3: Way Forward & Synthesis (3.5m - 5m)
   - Dual Input Modes: Keyboard text editor (word counter + Words-Per-Minute gauge) & Speech-to-Text with live audio waveform animation.
   - LocalStorage auto-save so answers are never lost.
5. **Objective AI Rubric Scoring (Total: 50 Points)**:
   - 🎯 **Factual Accuracy** (out of 10)
   - 📌 **Relevance & Thesis Adherence** (out of 10)
   - 🏛️ **Structure & Clarity** (out of 10)
   - 🔬 **Depth of Analysis** (out of 10)
   - ⏱️ **Time Discipline** (out of 10)
   - Detailed per-criterion feedback, overall feedback summary, and ideal UPSC model answer outline.
6. **MySQL Database & Historical Log**:
   - Automatically initializes `extempore_db` and tables (`users`, `categories`, `headlines_cache`, `practice_sessions`, `evaluations`).
   - Graceful local SQLite mirror fallback if MySQL credentials are not yet entered.
   - Live Database Settings modal in the web app to connect MySQL with one click.
   - Progress dashboard with metrics, streaks, average score, and searchable past session logs.

---

## 🚀 Quick Start

### 1. Run the Web Server
In PowerShell:
```powershell
cd C:\Users\AMAN\.gemini\antigravity\scratch\ai_extempore_app
python app.py
```
Or double-click `run.bat`.

### 2. Open in Your Browser
Navigate to:
```
http://127.0.0.1:5000
```

### 3. Connect to MySQL (Optional)
Click the **Database Status Pill** in the top-right corner of the website and enter your MySQL root password to link directly to your local MySQL 8.0 instance.
