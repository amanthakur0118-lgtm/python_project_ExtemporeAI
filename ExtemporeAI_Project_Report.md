# PROJECT REPORT
# ExtemporeAI: Real-Time AI-Powered Impromptu Speaking & Current Affairs Evaluation Platform

**Candidate / Developer**: Aman  
**Academic / Project Track**: Full-Stack AI & Public Speaking Coaching System  
**Version**: 1.5.0 Production  
**Live Application URL**: [https://aiextemporeapp.vercel.app](https://aiextemporeapp.vercel.app)  
**GitHub Repository**: [https://github.com/amanthakur0118-lgtm/python_project_ExtemporeAI](https://github.com/amanthakur0118-lgtm/python_project_ExtemporeAI)  
**Date**: October 2026  

---

## TABLE OF CONTENTS
1. [Abstract](#1-abstract)
2. [Introduction & Problem Statement](#2-introduction--problem-statement)
3. [Existing Systems & Literature Survey](#3-existing-systems--literature-survey)
4. [Proposed System Overview](#4-proposed-system-overview)
5. [System Architecture & Design](#5-system-architecture--design)
6. [Detailed Module Specifications](#6-detailed-module-specifications)
   - 6.1 Real-Time News Ingestion & Topic Synthesis Engine
   - 6.2 Dual Practice Modes (Breaking News & Custom Fresh Entry)
   - 6.3 Voice Recognition & Real-Time Pacing Arena
   - 6.4 50-Point UPSC Standardized Rubric & Anti-Hallucination Guards
   - 6.5 Daily Current Affairs MCQ Quiz Engine
   - 6.6 Relational Persistence & Analytics Layer
7. [Database Design & Schema](#7-database-design--schema)
8. [Deployment & Serverless Cloud Architecture](#8-deployment--serverless-cloud-architecture)
9. [Verification, Testing & Results](#9-verification-testing--results)
10. [Future Scope & Enhancements](#10-future-scope--enhancements)
11. [Conclusion](#11-conclusion)
12. [References & Appendix](#12-references--appendix)

---

## 1. ABSTRACT
Public speaking, and specifically impromptu (extempore) speaking, is one of the most intellectually demanding components of elite competitive examinations, including the Union Public Service Commission (UPSC) Civil Services Personality Test, Services Selection Board (SSB) lecturettes, MBA Group Discussions & Personal Interviews (GD/PI), and corporate leadership assessments. Candidates are typically given an unfamiliar contemporary motion and allowed 60 seconds of preparation before delivering an articulate, balanced, and evidence-grounded 3- to 5-minute discourse.

Traditional coaching methodologies suffer from severe structural limitations: human evaluation is expensive, unstandardized, and scheduling-constrained, while self-study lacks objective real-time speech analytics and feedback on factual accuracy. Furthermore, conventional mock questions are static and fail to reflect daily breaking geopolitical, constitutional, and economic developments.

To address these challenges, **ExtemporeAI** was conceived and engineered. ExtemporeAI is a production-grade, full-stack web platform powered by Python (Flask), Google Gemini GenAI, the Web Speech API, and a resilient dual MySQL/SQLite relational database architecture. The system automatically ingests real-time RSS news feeds across six high-yield domains, synthesizes multi-perspective debate motions, captures candidate speech via client-side speech-to-text recognition, enforces real-time pacing discipline, and grades transcripts against a rigorous 50-point UPSC rubric. Additionally, an interactive Daily Current Affairs MCQ Quiz arena provides timed retention drills. The platform is deployed live on Vercel Serverless infrastructure with global availability.

---

## 2. INTRODUCTION & PROBLEM STATEMENT

### 2.1 Background
The ability to formulate, structure, and articulate complex policy positions under extreme cognitive time pressure is the hallmark of effective administrative leaders and executives. In UPSC interviews and corporate assessments, evaluators look for:
1. **Immediate Cognitive Recall**: Retrieving relevant constitutional articles, statutory precedents, economic indicators, and historical treaties without reference notes.
2. **Structural Coherence**: Delivering an intuitive three-part speech (Introduction, Multi-stakeholder Body Analysis, Constructive Conclusion).
3. **Pacing & Vocal Composure**: Speaking between 110 and 150 Words Per Minute (WPM) without verbal crutches or panic pauses.
4. **Nuanced Neutrality**: Analyzing both pros and cons rather than adopting polarizing ideological rhetoric.

### 2.2 The Problem Statement
Existing learning pathways fail candidates across three critical dimensions:
- **The Evaluation Void**: Candidates practice alone into a voice recorder or mirror. Without real-time transcription and semantic analysis, they have no objective means of measuring relevance, factual accuracy, or structural balance.
- **The Stale Knowledge Barrier**: Preparing with static textbooks or past year papers disconnects candidates from dynamic current affairs (e.g., semiconductor trade agreements, emerging Supreme Court constitutional benches, or RBI monetary changes).
- **Prohibitive Mentorship Costs**: One-on-one mock interview sessions with veteran civil servants or communications trainers cost upwards of $100 per hour, creating a steep socio-economic barrier for underprivileged aspirants.

### 2.3 Project Objectives
The objective of this project is to build an autonomous, zero-cost, real-time coaching ecosystem that:
1. Dynamically curates daily high-yield news headlines across six strategic categories.
2. Synthesizes balanced extempore debate prompts with multi-dimensional context dossiers.
3. Provides a high-fidelity exam simulation environment featuring 60-second preparation and 5-minute timed speaking phases.
4. Employs client-side speech recognition with continuous WPM calculation and visual pacing guidance.
5. Applies a strict, 50-point UPSC-standardized rubric with automated safeguards against hallucination, incoherence, and off-topic digression.
6. Delivers an interactive, timed Current Affairs MCQ Quiz arena with educational answer explanations.
7. Guarantees 99.9% uptime and zero-cost scaling via serverless cloud deployment.

---

## 3. EXISTING SYSTEMS & LITERATURE SURVEY

| Feature / Dimension | Traditional Human Coaching | Generic Voice Recorders / Toastmasters | Generic LLM Chatbots (ChatGPT/Claude) | **ExtemporeAI (Proposed System)** |
| :--- | :--- | :--- | :--- | :--- |
| **Availability** | Low (By appointment only) | High (Manual recording) | High (Text interface) | **Instant, 24/7 Global Access** |
| **Real-Time News Ingestion** | Dependent on mentor prep | None (User must bring topic) | Static knowledge cutoff / Manual search | **Automated Zero-Dependency Live RSS** |
| **Exam Timer Simulation** | Manual stopwatch | Self-monitored | None (Un-timed chat) | **Precision 60s Prep + 5m Timed Arena** |
| **Speech-to-Text Transcription** | None | Manual playback | Requires manual audio upload | **Low-Latency In-Browser Web Speech STT** |
| **Pacing & Speedometer** | Subjective human comment | None | None | **Live WPM Gauge & Pacing Guidance** |
| **Standardized Rubric** | Subjective, mentor-biased | Basic peer feedback | Generic text review | **Strict 50-Pt UPSC Standardized Rubric** |
| **Incoherence / Anti-Cheat Guard** | Human detects immediately | N/A | Often flatters/generates false praise | **Rigorous Penalty Guard (<5/50 for junk)** |
| **MCQ Drill Integration** | Separate test series | None | Requires manual prompt engineering | **Built-in 5-Question Timed MCQ Arena** |
| **Cost** | High ($50 - $200/hr) | Free / Low | $20/month subscription | **100% Free & Open Source** |

---

## 4. PROPOSED SYSTEM OVERVIEW

ExtemporeAI is built upon a modular, event-driven, three-tier architecture:

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER (SPA)                                 |
|  - Launchpad & News Feed        - Preparation Scratchpad      - 5-Min Timed Arena |
|  - Web Speech API (STT)         - Pacing Speedometer (WPM)    - SVG Countdown Ring|
|  - Audio Visualizer             - Acoustic Sound Effects      - Daily MCQ Arena   |
+------------------------------------------+----------------------------------------+
                                           | HTTPS / JSON REST API
                                           v
+-----------------------------------------------------------------------------------+
|                             APPLICATION LAYER (Flask)                             |
|  - app.py: REST Endpoints & Router                - config.py: Multi-Env Config   |
|  - news_service.py: RSS Ingestion & XML Parsing   - ai_service.py: Rubric Engine  |
|  - quiz_service.py: 6-Domain MCQ Generator        - database.py: Relational DAO   |
+------------------------------------------+----------------------------------------+
                                           | SQL Queries / Transactions
                                           v
+-----------------------------------------------------------------------------------+
|                              DATA TIER (Dual Mirror)                              |
|  - Primary: MySQL 8.0 (extempore_db) with Foreign Keys & Cascading Deletes        |
|  - Fallback Mirror: SQLite 3 with automatic /tmp/ redirection on Vercel           |
|  - Tables: users, categories, headlines_cache, practice_sessions, evaluations,     |
|            quiz_results                                                           |
+-----------------------------------------------------------------------------------+
```

---

## 5. DETAILED MODULE SPECIFICATIONS

### 5.1 Real-Time News Ingestion & Topic Synthesis Engine (`news_service.py`, `ai_service.py`)
- **RSS Ingestion**: Pulls raw XML feeds from Google News across six distinct categories:
  1. *National & Polity*: Parliamentary legislation, constitutional debates, Election Commission guidelines.
  2. *International Relations*: Quad summits, bilateral defense partnerships, Indo-Pacific diplomacy.
  3. *Tech & Cyber Governance*: Semiconductor fabrication, AI safety regulation, digital data protection.
  4. *Economy & Banking*: Inflation targeting, fiscal deficit, trade balances, GST council updates.
  5. *Sports & Society*: Sports infrastructure, public health, gender equality initiatives.
  6. *General Mix*: Cross-disciplinary contemporary dilemmas.
- **Topic Formulation**: Transforms raw news headlines into provocative, open-ended extempore motions using standard civil service directive verbs (*"Critically analyze..."*, *"Evaluate the ramifications of..."*).
- **Context Dossier**: Generates a 3-point briefing outlining Constitutional Background, Economic Stakeholder Trade-offs, and International Precedents.

### 5.2 Dual Practice Modes: Breaking News & Custom Fresh Entry
- **Breaking News Mode**: Candidates pick from real-time live headlines refreshed directly from global publications.
- **Custom Fresh Entry Mode**: Candidates can input their own motion or select from curated trending chips (*One Nation One Election*, *AI & Job Displacement*, *Uniform Civil Code*, *Climate Justice*, *Digital Sovereignty*).
- **Instant Clean Reset**: Clicking **➕ Fresh Entry** in the top navigation immediately halts active timers, stops audio streaming, clears scratchpad buffers, and provides a visual toast confirmation.

### 5.3 Voice Recognition & Real-Time Pacing Arena (`speech.js`, `timer.js`)
- **Client-Side Speech-to-Text**: Employs the HTML5 Web Speech API (`webkitSpeechRecognition`) in continuous listening mode with interim results.
- **Dynamic Speedometer**: Continuously tracks elapsed speaking time against transcript word count to calculate instantaneous and rolling Words Per Minute (WPM):
  - `< 100 WPM`: Flagged as **Slow / Hesitant** (amber warning).
  - `110 - 150 WPM`: Flagged as **Optimal / Articulate** (emerald green).
  - `> 160 WPM`: Flagged as **Rushed / Breathless** (rose red warning).
- **Acoustic Audio Signals**: Built using the Web Audio API without external audio files:
  - 5-second gentle preparatory chime (`440 Hz Sine wave with exponential decay`).
  - Final examination buzzer (`220 Hz Sawtooth dual-tone alert`).

### 5.4 50-Point UPSC Standardized Rubric Scoring Engine (`ai_service.py`)
Each candidate transcript is evaluated across five distinct 10-point dimensions:
1. **Factual Accuracy & Context (10 Pts)**: Verification of statutory provisions, court rulings, empirical data, and international treaties.
2. **Relevance & Direct Focus (10 Pts)**: Measures direct adherence to the core question; penalizes discursive tangents.
3. **Structure & Clarity (10 Pts)**: Evaluates tripartite coherence (Introduction, Body, Conclusion).
4. **Depth of Analysis (10 Pts)**: Assesses multi-stakeholder trade-offs, socio-economic impact, and strategic feasibility.
5. **Time Discipline & Pacing (10 Pts)**: Rewards sustained delivery within optimal WPM ranges; penalizes premature termination.

#### Strict Anti-Hallucination & Quality Guards:
- **Incoherence / Random Gibberish Filter**: Inputs like *"banana potato asdf"* are detected by statistical language modeling and awarded `< 5 / 50` with an explicit Disqualified / Incoherent status.
- **Off-Topic Detection**: Answering a constitutional question with sports trivia incurs a penalty, dropping Relevance and Depth to `1 / 10`.
- **Ideal Model Answer Generation**: Generates a gold-standard UPSC benchmark response highlighting constitutional articles and policy roadmaps.

### 5.5 Daily Current Affairs MCQ Quiz Engine (`quiz_service.py`)
- **Domain Drills**: Generates 5-question rapid drills across any chosen domain or all domains combined.
- **45-Second Countdown Ring**: Enforces rapid recall under pressure.
- **Instant Option Feedback**: Clicked options light up dynamically: correct answers glow emerald green; wrong choices glow crimson red.
- **Educational Rationales**: Immediately reveals an in-depth explanatory breakdown detailing why the correct option is valid and providing historical context.
- **Persistent Tracking**: Quiz scores, accuracy percentage, and time taken are written to the database.

---

## 6. DATABASE DESIGN & SCHEMA

The database schema (`schema.sql`) enforces relational integrity with foreign keys and cascading deletes:

```sql
-- 1. Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Categories Table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50) DEFAULT 'mic'
);

-- 3. Practice Sessions Table
CREATE TABLE practice_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT,
    motion TEXT NOT NULL,
    preparation_duration INT DEFAULT 60,
    speaking_duration INT DEFAULT 300,
    transcript TEXT,
    words_per_minute FLOAT DEFAULT 0.0,
    total_words INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- 4. Evaluations Table
CREATE TABLE evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL UNIQUE,
    score_accuracy INT NOT NULL,
    score_relevance INT NOT NULL,
    score_structure INT NOT NULL,
    score_depth INT NOT NULL,
    score_pacing INT NOT NULL,
    total_score INT NOT NULL,
    orator_tier VARCHAR(50) NOT NULL,
    feedback_strengths TEXT,
    feedback_improvements TEXT,
    model_structure TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE
);

-- 5. Quiz Results Table
CREATE TABLE quiz_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    domain VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    total_questions INT DEFAULT 5,
    accuracy_pct FLOAT NOT NULL,
    time_taken_seconds INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Dual MySQL & SQLite Mirror Architecture:
To guarantee that the application runs locally and on cloud serverless environments without requiring external database provisioning:
- **MySQL Primary**: Used when `MYSQL_HOST` and credentials are provided in `.env`.
- **SQLite Mirror**: Automatically initializes when MySQL is unavailable.
- **Serverless Read-Only Filesystem Handling**: In serverless containers (Vercel/AWS Lambda), the root filesystem is read-only. `config.py` detects `VERCEL=1` and dynamically redirects database writes to `/tmp/extempore_backup.db`.

---

## 7. DEPLOYMENT & CLOUD ARCHITECTURE

### 7.1 Serverless Deployment on Vercel
The application is deployed using `@vercel/python` on Vercel:
- **Configuration (`vercel.json`)**:
  ```json
  {
    "version": 2,
    "builds": [
      {
        "src": "app.py",
        "use": "@vercel/python"
      }
    ],
    "routes": [
      {
        "src": "/(.*)",
        "dest": "app.py"
      }
    ]
  }
  ```
- **Byte-Order Mark (BOM) Resolution**: The configuration file was strictly encoded in pure UTF-8 without BOM (`\xef\xbb\xbf`), resolving Vercel CLI JSON parse errors.
- **Package Compilation**: Dependencies (`Flask`, `PyMySQL`, `cryptography`, `requests`, `python-dotenv`, `google-genai`) are compiled via `uv` in under 5 seconds.
- **Live Deployment URL**: `https://aiextemporeapp.vercel.app`

### 7.2 GitHub Continuous Integration
- Repository: `https://github.com/amanthakur0118-lgtm/python_project_ExtemporeAI`
- Branch: `main`
- Automatic commit pushes trigger instant redeployments on Vercel.

---

## 8. VERIFICATION, TESTING & RESULTS

| Test Case ID | Subsystem / Action | Input / Condition | Expected Behavior | Observed Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Web Application Shell | `GET /` | Returns HTML shell with dark theme | HTTP 200 OK | **PASS** |
| **TC-02** | Category Hierarchy | `GET /api/categories` | Returns 6 taxonomy domains | HTTP 200 OK (6 loaded) | **PASS** |
| **TC-03** | Live RSS Ingestion | `GET /api/news/polity` | Pulls Google News XML | HTTP 200 OK (5+ headlines) | **PASS** |
| **TC-04** | Topic Formulation | `POST /api/generate-question` | Domain headline input | Returns balanced debate motion | HTTP 200 OK | **PASS** |
| **TC-05** | Rubric Incoherence Guard | `POST /api/evaluate` | Input: `"asdf banana potato"` | Score < 5/50; Disqualified status | HTTP 200 OK (Score: 2/50) | **PASS** |
| **TC-06** | Rubric Off-Topic Guard | `POST /api/evaluate` | Sports speech on Legal topic | Relevance penalized to 1/10 | HTTP 200 OK (Score: 10/50) | **PASS** |
| **TC-07** | Rubric High Quality | `POST /api/evaluate` | Structured constitutional speech | Score > 35/50; Distinguished tier | HTTP 200 OK (Score: 40/50) | **PASS** |
| **TC-08** | Daily Quiz API | `GET /api/quiz?domain=polity`| Domain filter query | Returns 5 randomized MCQs | HTTP 200 OK (5 questions) | **PASS** |
| **TC-09** | Quiz Scoring & Storage | `POST /api/quiz/submit` | 5 user answers + time taken | Computes accuracy & saves to DB | HTTP 200 OK (DB written) | **PASS** |
| **TC-10** | Database Persistence | `GET /api/history` | User session query | Returns historical drills | HTTP 200 OK | **PASS** |
| **TC-11** | Vector Favicon Delivery | `GET /favicon.ico` | Direct icon request | Returns SVG/ICO icon | HTTP 200 OK (`image/svg+xml`)| **PASS** |
| **TC-12** | JS Syntax Validation | Node compiler | `node -c static/js/app.js` | Zero syntax errors | Exit Code 0 (0 errors) | **PASS** |
| **TC-13** | DOM ID Audit | Python parser | Audit 119 script ID references | 0 missing DOM elements in HTML | 100% Validated (0 missing)| **PASS** |
| **TC-14** | Cloud Production | `GET https://aiextemporeapp.vercel.app` | Global HTTPS request | Live Vercel serverless response | HTTP 200 OK | **PASS** |

---

## 9. FUTURE SCOPE & ENHANCEMENTS

1. **Acoustic Audio Prosody & Pitch Analysis**:
   - Integrating Fast Fourier Transform (FFT) analysis on recorded audio to detect pitch variation, vocal enthusiasm, and nervous vocal tremors.
2. **Computer Vision & Non-Verbal Communication Tracking**:
   - Integrating lightweight WebRTC and MediaPipe computer vision to evaluate camera eye-contact, facial composure, and open hand gestures.
3. **Multi-Agent Group Discussion (GD) Simulation**:
   - Deploying multiple LLM-driven autonomous peer avatars that simulate rival candidates in an MBA or corporate GD chamber, interjecting with counterarguments.
4. **Offline Progressive Web App (PWA)**:
   - Service Worker caching to allow practice drills and mock recording in low-connectivity areas.

---

## 10. CONCLUSION

ExtemporeAI bridges the divide between passive news consumption and active public speaking eloquence. By uniting real-time news scraping, client-side speech recognition, rigorous 50-point UPSC rubric evaluation with anti-hallucination safeguards, and an interactive Daily MCQ Quiz mode, the platform provides candidates with an accessible, high-yield training ground. Deployed globally on Vercel with zero server overhead and open-sourced on GitHub, ExtemporeAI establishes a modern benchmark for autonomous conversational AI coaching platforms.

---

## 11. APPENDIX & REPOSITORY DETAILS

- **Live Production URL**: [https://aiextemporeapp.vercel.app](https://aiextemporeapp.vercel.app)
- **GitHub Repository**: [https://github.com/amanthakur0118-lgtm/python_project_ExtemporeAI](https://github.com/amanthakur0118-lgtm/python_project_ExtemporeAI)
- **PowerPoint Presentation**: [`ExtemporeAI_Presentation.pptx`](file:///C:/Users/AMAN/.gemini/antigravity/scratch/ai_extempore_app/ExtemporeAI_Presentation.pptx)
- **Interactive Presentation Deck**: [`ExtemporeAI_Presentation.html`](file:///C:/Users/AMAN/.gemini/antigravity/scratch/ai_extempore_app/ExtemporeAI_Presentation.html)
- **Printable HTML Report**: [`ExtemporeAI_Project_Report.html`](file:///C:/Users/AMAN/.gemini/antigravity/scratch/ai_extempore_app/ExtemporeAI_Project_Report.html)
- **Local Quickstart**: Double-click `run.bat` in the project root directory.
