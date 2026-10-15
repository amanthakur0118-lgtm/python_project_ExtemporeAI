/* ==========================================================
   MAIN APPLICATION CONTROLLER
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // Application State
    const state = {
        selectedCategory: 'polity',
        categoryName: 'National & Polity (UPSC)',
        selectedHeadline: '',
        selectedSource: 'Live News',
        generatedQuestion: '',
        prepDuration: 60,
        answerDuration: 300,
        inputMode: 'text',
        scratchpadText: '',
        timeStarted: 0
    };

    const timer = new ExtemporeTimer();
    let speechManager = null;

    // DOM Elements
    const views = {
        launchpad: document.getElementById('view-launchpad'),
        prep: document.getElementById('view-prep'),
        arena: document.getElementById('view-arena'),
        results: document.getElementById('view-results'),
        analytics: document.getElementById('view-analytics')
    };

    const navButtons = document.querySelectorAll('.nav-btn');
    const categoryCards = document.querySelectorAll('.category-card');
    const headlinesList = document.getElementById('headlines-list');
    const btnLaunch = document.getElementById('btn-launch');
    const btnSkipPrep = document.getElementById('btn-skip-prep');
    const btnSubmitAnswer = document.getElementById('btn-submit-answer');
    const answerTextarea = document.getElementById('answer-textarea');
    const scratchpad = document.getElementById('scratchpad-notes');
    const liveWordCount = document.getElementById('live-word-count');
    const liveWpm = document.getElementById('live-wpm');
    const arenaTimerBadge = document.getElementById('arena-timer-badge');
    const prepSecondsDisplay = document.getElementById('prep-seconds-display');
    const radialProgress = document.getElementById('radial-timer-progress');
    const newsTickerText = document.getElementById('ticker-headline-text');

    // Modals
    const dbModal = document.getElementById('db-modal');
    const sessionModal = document.getElementById('session-detail-modal');

    // Toast Notification System
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast ${type === 'success' ? 'toast-success' : 'toast-info'}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(15px)';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ----------------------------------------------------------
    // VIEW SWITCHING
    // ----------------------------------------------------------
    function switchView(viewName) {
        Object.keys(views).forEach(k => {
            if (views[k]) {
                views[k].classList.remove('active-view');
            }
        });
        if (views[viewName]) {
            views[viewName].classList.add('active-view');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Update nav buttons
        navButtons.forEach(btn => {
            if (btn.dataset.view === viewName) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        if (viewName === 'analytics') {
            loadAnalyticsData();
            loadHistoryTable();
        }
    }

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetView = btn.dataset.view;
            if (targetView) {
                switchView(targetView);
            }
        });
    });

    // ----------------------------------------------------------
    // THEME TOGGLE (Dark / Light)
    // ----------------------------------------------------------
    const themeToggleBtn = document.getElementById('btn-theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            themeToggleBtn.textContent = newTheme === 'dark' ? '🌙' : '☀️';
            localStorage.setItem('extempore_theme', newTheme);
        });
        const savedTheme = localStorage.getItem('extempore_theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
            themeToggleBtn.textContent = savedTheme === 'dark' ? '🌙' : '☀️';
        }
    }

    // ----------------------------------------------------------
    // SPEECH RECOGNITION SETUP
    // ----------------------------------------------------------
    const btnMic = document.getElementById('btn-mic-toggle');
    const voicePanel = document.getElementById('voice-panel');
    const micStatusText = document.getElementById('mic-status-text');

    speechManager = new SpeechInputManager(
        (finalTranscript, interimTranscript) => {
            if (finalTranscript) {
                const currentVal = answerTextarea.value;
                answerTextarea.value = (currentVal + ' ' + finalTranscript).trim();
                updateAnswerMetrics();
            }
        },
        (isRecording) => {
            if (isRecording) {
                voicePanel.classList.add('active');
                voicePanel.classList.add('recording');
                btnMic.innerHTML = '🛑 Stop Recording';
                btnMic.style.background = 'var(--accent-amber)';
                micStatusText.textContent = 'Listening... Speak clearly into your microphone.';
            } else {
                voicePanel.classList.remove('recording');
                btnMic.innerHTML = '🎙️ Start Voice Input';
                btnMic.style.background = 'var(--accent-rose)';
                micStatusText.textContent = 'Microphone paused. Click to resume.';
            }
        }
    );

    if (btnMic) {
        btnMic.addEventListener('click', () => {
            speechManager.toggle();
        });
    }

    // Mode Toggle Pills in Workspace (Text vs Voice)
    const modeToggles = document.querySelectorAll('.mode-toggle-btn');
    modeToggles.forEach(btn => {
        btn.addEventListener('click', () => {
            modeToggles.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const mode = btn.dataset.mode;
            state.inputMode = mode;
            if (mode === 'voice') {
                voicePanel.classList.add('active');
                speechManager.start();
            } else {
                speechManager.stop();
                voicePanel.classList.remove('active');
            }
        });
    });

    // ----------------------------------------------------------
    // CATEGORY SELECTION & HEADLINE FETCHING
    // ----------------------------------------------------------
    categoryCards.forEach(card => {
        card.addEventListener('click', () => {
            categoryCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            state.selectedCategory = card.dataset.slug;
            state.categoryName = card.dataset.name;
            fetchHeadlines(state.selectedCategory);
        });
    });

    async function fetchHeadlines(categorySlug) {
        headlinesList.innerHTML = '<div style="padding:1rem;color:var(--text-muted);text-align:center;">Fetching live breaking headlines...</div>';
        try {
            const resp = await fetch(`/api/news/${categorySlug}`);
            const data = await resp.json();
            headlinesList.innerHTML = '';

            if (data.headlines && data.headlines.length > 0) {
                // Update top ticker
                newsTickerText.innerHTML = `<b>${data.headlines[0].source}:</b> ${data.headlines[0].headline}`;

                data.headlines.forEach((item, idx) => {
                    const row = document.createElement('div');
                    row.className = `headline-item ${idx === 0 ? 'selected' : ''}`;
                    if (idx === 0) {
                        state.selectedHeadline = item.headline;
                        state.selectedSource = item.source;
                    }

                    row.innerHTML = `
                        <div class="headline-text">${item.headline}</div>
                        <div class="headline-meta">${item.source} • ${item.published}</div>
                    `;

                    row.addEventListener('click', () => {
                        document.querySelectorAll('.headline-item').forEach(h => h.classList.remove('selected'));
                        row.classList.add('selected');
                        state.selectedHeadline = item.headline;
                        state.selectedSource = item.source;
                    });

                    headlinesList.appendChild(row);
                });
            } else {
                headlinesList.innerHTML = '<div style="padding:1rem;color:var(--text-muted);">No headlines found. A curated topic will be chosen.</div>';
            }
        } catch (e) {
            headlinesList.innerHTML = '<div style="padding:1rem;color:var(--text-rose);">Notice: Failed to fetch live headlines. Fallback active.</div>';
        }
    }

    // Config Option Pills (Prep time, Answer time)
    document.querySelectorAll('.pill-option[data-prep]').forEach(pill => {
        pill.addEventListener('click', () => {
            pill.parentElement.querySelectorAll('.pill-option').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.prepDuration = parseInt(pill.dataset.prep);
        });
    });

    document.querySelectorAll('.pill-option[data-answer]').forEach(pill => {
        pill.addEventListener('click', () => {
            pill.parentElement.querySelectorAll('.pill-option').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            state.answerDuration = parseInt(pill.dataset.answer);
        });
    });

    // ----------------------------------------------------------
    // TOPIC SELECTION TABS: RSS VS CUSTOM FRESH ENTRY
    // ----------------------------------------------------------
    const tabTopicRss = document.getElementById('tab-topic-rss');
    const tabTopicCustom = document.getElementById('tab-topic-custom');
    const panelTopicRss = document.getElementById('panel-topic-rss');
    const panelTopicCustom = document.getElementById('panel-topic-custom');
    const customTopicInput = document.getElementById('custom-topic-input');
    const presetChips = document.querySelectorAll('.preset-chip');

    function selectTopicTab(mode) {
        if (mode === 'custom') {
            if (tabTopicCustom) tabTopicCustom.classList.add('active');
            if (tabTopicRss) tabTopicRss.classList.remove('active');
            if (panelTopicCustom) panelTopicCustom.style.display = 'block';
            if (panelTopicRss) panelTopicRss.style.display = 'none';
            if (customTopicInput && customTopicInput.value.trim()) {
                state.selectedHeadline = customTopicInput.value.trim();
                state.selectedSource = 'Custom Candidate Motion';
            }
        } else {
            if (tabTopicRss) tabTopicRss.classList.add('active');
            if (tabTopicCustom) tabTopicCustom.classList.remove('active');
            if (panelTopicRss) panelTopicRss.style.display = 'block';
            if (panelTopicCustom) panelTopicCustom.style.display = 'none';
        }
    }

    if (tabTopicRss) tabTopicRss.addEventListener('click', () => selectTopicTab('rss'));
    if (tabTopicCustom) tabTopicCustom.addEventListener('click', () => {
        selectTopicTab('custom');
        if (customTopicInput) customTopicInput.focus();
    });

    if (customTopicInput) {
        customTopicInput.addEventListener('input', () => {
            const val = customTopicInput.value.trim();
            if (val) {
                state.selectedHeadline = val;
                state.selectedSource = 'Custom Candidate Motion';
            }
        });
    }

    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            presetChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            const topic = chip.dataset.topic;
            if (customTopicInput) {
                customTopicInput.value = topic;
                customTopicInput.focus();
            }
            state.selectedHeadline = topic;
            state.selectedSource = 'Custom Candidate Motion';
            showToast(`Loaded topic: "${topic.substring(0, 36)}..."`, 'info');
        });
    });

    // ----------------------------------------------------------
    // LAUNCH ARENA (QUESTION GENERATION -> PREP)
    // ----------------------------------------------------------
    if (btnLaunch) {
        btnLaunch.addEventListener('click', async () => {
            let headlineToSend = state.selectedHeadline;
            let sourceToSend = state.selectedSource;

            // If on custom tab, validate input
            if (panelTopicCustom && panelTopicCustom.style.display !== 'none') {
                if (customTopicInput && customTopicInput.value.trim()) {
                    headlineToSend = customTopicInput.value.trim();
                    sourceToSend = 'Custom Candidate Motion';
                } else {
                    alert('Please type a custom topic or click one of the quick trending themes above.');
                    if (customTopicInput) customTopicInput.focus();
                    return;
                }
            }

            btnLaunch.disabled = true;
            btnLaunch.innerHTML = '⚡ Formulating Challenge Question...';

            try {
                const resp = await fetch('/api/generate-question', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        headline: headlineToSend,
                        source: sourceToSend,
                        category: state.selectedCategory
                    })
                });

                const data = await resp.json();
                state.generatedQuestion = data.question;
                state.selectedHeadline = data.headline;
                state.selectedSource = data.source;

                // Populate Prep Screen
                const pq = document.getElementById('prep-question-text');
                const ps = document.getElementById('prep-source-tag');
                const ph = document.getElementById('prep-headline-snippet');
                if (pq) pq.textContent = state.generatedQuestion;
                if (ps) ps.textContent = `📰 Source: ${state.selectedSource}`;
                if (ph) ph.textContent = `Headline: "${state.selectedHeadline}"`;
                if (scratchpad) scratchpad.value = '';

                switchView('prep');
                startPrepPhase();
            } catch (e) {
                alert('Could not generate question. Please try again.');
            } finally {
                btnLaunch.disabled = false;
                btnLaunch.innerHTML = 'Generate Topic & Start Prep ⚡';
            }
        });
    }

    // ----------------------------------------------------------
    // PREPARATION PHASE (30s - 60s)
    // ----------------------------------------------------------
    const circumference = 2 * Math.PI * 90; // approx 565.48
    if (radialProgress) {
        radialProgress.style.strokeDasharray = `${circumference} ${circumference}`;
    }

    function startPrepPhase() {
        timer.start(state.prepDuration, (remaining, total) => {
            prepSecondsDisplay.textContent = remaining;
            const progressRatio = remaining / total;
            const offset = circumference - (progressRatio * circumference);
            radialProgress.style.strokeDashoffset = offset;

            if (progressRatio <= 0.2) {
                radialProgress.style.stroke = 'var(--accent-rose)';
            } else if (progressRatio <= 0.4) {
                radialProgress.style.stroke = 'var(--accent-amber)';
            } else {
                radialProgress.style.stroke = 'var(--accent-emerald)';
            }
        }, () => {
            // Prep completed -> jump directly to Answer Arena
            startAnswerPhase();
        });
    }

    if (btnSkipPrep) {
        btnSkipPrep.addEventListener('click', () => {
            timer.stop();
            startAnswerPhase();
        });
    }

    // ----------------------------------------------------------
    // ANSWER PHASE (5 MINUTES TIMED WINDOW)
    // ----------------------------------------------------------
    function startAnswerPhase() {
        state.scratchpadText = scratchpad ? scratchpad.value : '';
        state.timeStarted = Date.now();
        if (answerTextarea) answerTextarea.value = '';
        updateAnswerMetrics();

        // Populate arena question header
        const aq = document.getElementById('arena-question-snippet');
        if (aq) aq.textContent = state.generatedQuestion;

        switchView('arena');

        // Check if scratchpad had notes and place them as helper placeholder or comment
        const ar = document.getElementById('arena-scratchpad-reminder');
        if (ar) {
            if (state.scratchpadText.trim()) {
                ar.textContent = `Your notes: ${state.scratchpadText}`;
            } else {
                ar.textContent = '';
            }
        }

        timer.start(state.answerDuration, (remaining, total) => {
            if (arenaTimerBadge) {
                arenaTimerBadge.textContent = ExtemporeTimer.formatTime(remaining);
                if (remaining <= 30) {
                    arenaTimerBadge.className = 'live-timer-badge danger';
                } else if (remaining <= 90) {
                    arenaTimerBadge.className = 'live-timer-badge warning';
                } else {
                    arenaTimerBadge.className = 'live-timer-badge';
                }
            }

            // Pacing bar segment highlights
            const timeElapsed = total - remaining;
            const elapsedPercent = (timeElapsed / total) * 100;

            const seg1 = document.getElementById('pacing-seg-1');
            const seg2 = document.getElementById('pacing-seg-2');
            const seg3 = document.getElementById('pacing-seg-3');
            const lbl1 = document.getElementById('pacing-lbl-1');
            const lbl2 = document.getElementById('pacing-lbl-2');
            const lbl3 = document.getElementById('pacing-lbl-3');

            [seg1, seg2, seg3, lbl1, lbl2, lbl3].forEach(el => el && el.classList.remove('active'));

            if (elapsedPercent <= 20) {
                seg1 && seg1.classList.add('active');
                lbl1 && lbl1.classList.add('active');
            } else if (elapsedPercent <= 70) {
                seg2 && seg2.classList.add('active');
                lbl2 && lbl2.classList.add('active');
            } else {
                seg3 && seg3.classList.add('active');
                lbl3 && lbl3.classList.add('active');
            }
        }, () => {
            // Hard auto-submit when timer hits 00:00!
            submitAnswerForEvaluation(true);
        });
    }

    if (answerTextarea) {
        answerTextarea.addEventListener('input', () => {
            updateAnswerMetrics();
            localStorage.setItem('extempore_draft', answerTextarea.value);
        });
    }

    function updateAnswerMetrics() {
        if (!answerTextarea) return;
        const text = answerTextarea.value.trim();
        const words = text ? text.split(/\s+/).length : 0;
        if (liveWordCount) liveWordCount.textContent = `${words} words`;

        const secondsPassed = Math.max(1, Math.floor((Date.now() - state.timeStarted) / 1000));
        const minutesPassed = secondsPassed / 60;
        const wpm = Math.round(words / minutesPassed);
        if (liveWpm) liveWpm.textContent = `${wpm} WPM`;
    }

    if (btnSubmitAnswer) {
        btnSubmitAnswer.addEventListener('click', () => {
            if (!answerTextarea || !answerTextarea.value.trim()) {
                alert('Please speak or type your answer before submitting.');
                return;
            }
            const timeRemaining = timer.timeRemaining;
            if (timeRemaining > 60) {
                if (!confirm(`You still have ${ExtemporeTimer.formatTime(timeRemaining)} remaining. Are you sure you want to finish and submit now?`)) {
                    return;
                }
            }
            submitAnswerForEvaluation(false);
        });
    }

    async function submitAnswerForEvaluation(isAutoSubmit = false) {
        timer.stop();
        speechManager.stop();

        const answerText = answerTextarea.value.trim() || "(Candidate did not record an answer before time elapsed)";
        const timeTaken = timer.getTimeTaken();

        btnSubmitAnswer.disabled = true;
        btnSubmitAnswer.innerHTML = '⏳ AI Examiner is Evaluating Against Rubric...';

        try {
            const resp = await fetch('/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: state.generatedQuestion,
                    headline: state.selectedHeadline,
                    category_name: state.categoryName,
                    source_name: state.selectedSource,
                    user_answer: answerText,
                    prep_time: state.prepDuration,
                    answer_time: state.answerDuration,
                    time_taken: timeTaken,
                    input_mode: state.inputMode,
                    scratchpad: state.scratchpadText
                })
            });

            const data = await resp.json();
            if (data.evaluation) {
                renderScorecard(data.evaluation, answerText, timeTaken);
                switchView('results');
                localStorage.removeItem('extempore_draft');
            } else {
                alert('Evaluation error: ' + (data.error || 'Server error'));
            }
        } catch (e) {
            alert('Submission failed. Check network or server status.');
        } finally {
            btnSubmitAnswer.disabled = false;
            btnSubmitAnswer.innerHTML = 'Submit & Grade Answer 🚀';
        }
    }

    // ----------------------------------------------------------
    // RENDER RUBRIC SCORECARD (50 POINTS TOTAL)
    // ----------------------------------------------------------
    function renderScorecard(evalData, answerText, timeTaken) {
        document.getElementById('total-score-val').textContent = evalData.total_score;
        document.getElementById('evaluator-badge').textContent = `Graded by: ${evalData.ai_evaluator_type || 'Rubric Examiner'}`;
        
        // Performance Tier Badge
        const tierBadge = document.getElementById('performance-tier-badge');
        const score = evalData.total_score;
        if (score >= 44) {
            tierBadge.textContent = '🌟 Distinguished Orator (UPSC Board Tier)';
            tierBadge.style.color = 'var(--accent-emerald)';
        } else if (score >= 36) {
            tierBadge.textContent = '🎯 Analytical & Articulate (Commended)';
            tierBadge.style.color = '#818cf8';
        } else if (score >= 28) {
            tierBadge.textContent = '📈 Good Potential (Structure Polish Needed)';
            tierBadge.style.color = 'var(--accent-amber)';
        } else {
            tierBadge.textContent = '🌱 Foundation Phase (Practice Time Discipline)';
            tierBadge.style.color = 'var(--accent-rose)';
        }

        // 5 Rubric Criteria
        const rubrics = [
            { key: 'factual', name: '🎯 Factual Accuracy', score: evalData.score_factual, feedback: evalData.factual_feedback },
            { key: 'relevance', name: '📌 Relevance & Thesis', score: evalData.score_relevance, feedback: evalData.relevance_feedback },
            { key: 'structure', name: '🏛️ Structure & Clarity', score: evalData.score_structure, feedback: evalData.structure_feedback },
            { key: 'depth', name: '🔬 Depth of Analysis', score: evalData.score_depth, feedback: evalData.depth_feedback },
            { key: 'time', name: '⏱️ Time Discipline', score: evalData.score_time, feedback: evalData.time_feedback }
        ];

        const rubricContainer = document.getElementById('rubric-cards-grid');
        rubricContainer.innerHTML = '';

        rubrics.forEach(r => {
            const card = document.createElement('div');
            card.className = 'rubric-card';
            const percent = (r.score / 10) * 100;
            card.innerHTML = `
                <div class="rubric-card-header">
                    <span class="rubric-name">${r.name}</span>
                    <span class="rubric-score-pill">${r.score} / 10</span>
                </div>
                <div class="rubric-progress">
                    <div class="rubric-progress-fill" style="width: ${percent}%;"></div>
                </div>
                <div class="rubric-feedback">${r.feedback}</div>
            `;
            rubricContainer.appendChild(card);
        });

        // Overall Feedback & Model Answer Outline
        document.getElementById('overall-feedback-text').textContent = evalData.overall_feedback;
        document.getElementById('model-answer-outline').textContent = evalData.model_answer_structure;
        document.getElementById('results-candidate-answer').textContent = answerText;
    }

    // Action button on results: Practice Another
    const btnPracticeAnother = document.getElementById('btn-practice-another');
    if (btnPracticeAnother) {
        btnPracticeAnother.addEventListener('click', () => {
            switchView('launchpad');
            fetchHeadlines(state.selectedCategory);
        });
    }

    // ----------------------------------------------------------
    // HISTORY & ANALYTICS (MYSQL)
    // ----------------------------------------------------------
    async function loadAnalyticsData() {
        try {
            const resp = await fetch('/api/analytics');
            const data = await resp.json();

            document.getElementById('stat-total-sessions').textContent = data.total_sessions || 0;
            document.getElementById('stat-avg-score').textContent = data.average_score ? `${data.average_score} / 50` : '0 / 50';
            document.getElementById('stat-total-words').textContent = data.total_words || 0;
            document.getElementById('stat-streak').textContent = `${data.streak_days || 0} Days`;
        } catch (e) {
            console.log('Error loading analytics:', e);
        }
    }

    async function loadHistoryTable() {
        const tbody = document.getElementById('history-table-body');
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:1rem;">Loading historical sessions from MySQL...</td></tr>';

        try {
            const resp = await fetch('/api/history');
            const data = await resp.json();
            tbody.innerHTML = '';

            if (data.history && data.history.length > 0) {
                data.history.forEach(item => {
                    const tr = document.createElement('tr');
                    const dateStr = item.created_at ? String(item.created_at).substring(0, 16) : '-';
                    const score = item.total_score !== null ? `${item.total_score} / 50` : 'N/A';

                    tr.innerHTML = `
                        <td><b>#${item.id}</b></td>
                        <td>${item.category_name}</td>
                        <td style="max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${item.question}">${item.question}</td>
                        <td><span class="badge-orator">${score}</span></td>
                        <td><button class="btn-secondary" style="padding:0.35rem 0.75rem;font-size:0.8rem;" onclick="viewSessionDetails(${item.id})">Inspect 📋</button></td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:1.5rem;">No practice sessions recorded yet. Complete a session to see MySQL history!</td></tr>';
            }
        } catch (e) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--accent-rose);padding:1.5rem;">Failed to load history from database.</td></tr>';
        }
    }

    window.viewSessionDetails = async function(sessionId) {
        try {
            const resp = await fetch(`/api/session/${sessionId}`);
            const data = await resp.json();
            if (data.session) {
                const s = data.session;
                document.getElementById('modal-session-title').textContent = `Practice Session #${s.id} — ${s.category_name}`;
                document.getElementById('modal-session-question').textContent = s.question;
                document.getElementById('modal-session-answer').textContent = s.user_answer;
                document.getElementById('modal-session-score').textContent = `${s.total_score} / 50`;
                document.getElementById('modal-session-fb').textContent = s.overall_feedback || 'No feedback';
                sessionModal.classList.add('open');
            }
        } catch (e) {
            alert('Could not retrieve session details.');
        }
    };

    // ----------------------------------------------------------
    // DATABASE STATUS & CONFIGURATION MODAL
    // ----------------------------------------------------------
    const dbStatusPill = document.getElementById('db-status-pill');
    const dbStatusText = document.getElementById('db-status-text');
    const btnCloseDbModal = document.getElementById('btn-close-db-modal');
    const btnSaveDbConfig = document.getElementById('btn-save-db-config');
    const btnCloseSessionModal = document.getElementById('btn-close-session-modal');

    async function checkDbStatus() {
        try {
            const resp = await fetch('/api/db-status');
            const data = await resp.json();
            if (data.is_mysql) {
                dbStatusPill.className = 'db-status-pill';
                dbStatusText.textContent = `MySQL Connected (${data.database})`;
            } else {
                dbStatusPill.className = 'db-status-pill fallback';
                dbStatusText.textContent = `Local DB (${data.db_type})`;
            }
        } catch (e) {}
    }

    if (dbStatusPill) {
        dbStatusPill.addEventListener('click', () => {
            dbModal.classList.add('open');
        });
    }

    if (btnCloseDbModal) {
        btnCloseDbModal.addEventListener('click', () => {
            dbModal.classList.remove('open');
        });
    }

    if (btnCloseSessionModal) {
        btnCloseSessionModal.addEventListener('click', () => {
            sessionModal.classList.remove('open');
        });
    }

    if (btnSaveDbConfig) {
        btnSaveDbConfig.addEventListener('click', async () => {
            const host = document.getElementById('db-host').value.trim();
            const port = document.getElementById('db-port').value.trim();
            const user = document.getElementById('db-user').value.trim();
            const password = document.getElementById('db-password').value;
            const db_name = document.getElementById('db-name').value.trim();

            btnSaveDbConfig.disabled = true;
            btnSaveDbConfig.textContent = 'Testing connection...';

            try {
                const resp = await fetch('/api/db-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ host, port, user, password, db_name })
                });
                const result = await resp.json();
                alert(result.message);
                if (result.success) {
                    dbModal.classList.remove('open');
                    checkDbStatus();
                }
            } catch (e) {
                alert('Connection error occurred.');
            } finally {
                btnSaveDbConfig.disabled = false;
                btnSaveDbConfig.textContent = 'Connect & Save to MySQL';
            }
        });
    }

    // ----------------------------------------------------------
    // AI ENGINE STATUS & CONFIGURATION MODAL
    // ----------------------------------------------------------
    const aiStatusPill = document.getElementById('ai-status-pill');
    const aiStatusText = document.getElementById('ai-status-text');
    const aiModal = document.getElementById('ai-modal');
    const btnCloseAiModal = document.getElementById('btn-close-ai-modal');
    const btnSaveAiConfig = document.getElementById('btn-save-ai-config');
    const aiCurrentModeBadge = document.getElementById('ai-current-mode-badge');
    const geminiApiKeyInput = document.getElementById('gemini-api-key-input');

    async function checkAiStatus() {
        try {
            const resp = await fetch('/api/ai-status');
            const data = await resp.json();
            if (data.has_gemini) {
                aiStatusPill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
                aiStatusPill.style.background = 'rgba(16, 185, 129, 0.12)';
                aiStatusPill.style.color = 'var(--accent-emerald)';
                aiStatusText.textContent = 'AI: Gemini 2.5 Flash';
                if (aiCurrentModeBadge) {
                    aiCurrentModeBadge.innerHTML = '🟢 <span style="color:var(--accent-emerald);">Gemini 2.5 Flash (Active LLM)</span>';
                }
            } else {
                aiStatusPill.style.borderColor = 'rgba(99, 102, 241, 0.4)';
                aiStatusPill.style.background = 'rgba(99, 102, 241, 0.12)';
                aiStatusPill.style.color = '#818cf8';
                aiStatusText.textContent = 'AI: Strict Rubric Guard';
                if (aiCurrentModeBadge) {
                    aiCurrentModeBadge.innerHTML = '🔵 <span style="color:#818cf8;">Strict Rubric Examiner (Quality Guard Active)</span>';
                }
            }
        } catch (e) {}
    }

    if (aiStatusPill) {
        aiStatusPill.addEventListener('click', () => {
            aiModal.classList.add('open');
            checkAiStatus();
        });
    }

    if (btnCloseAiModal) {
        btnCloseAiModal.addEventListener('click', () => {
            aiModal.classList.remove('open');
        });
    }

    if (btnSaveAiConfig) {
        btnSaveAiConfig.addEventListener('click', async () => {
            const key = geminiApiKeyInput.value.trim();
            btnSaveAiConfig.disabled = true;
            btnSaveAiConfig.textContent = 'Validating key with Google AI...';

            try {
                const resp = await fetch('/api/ai-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: key })
                });
                const res = await resp.json();
                alert(res.message);
                if (res.success) {
                    aiModal.classList.remove('open');
                    checkAiStatus();
                }
            } catch (e) {
                alert('Connection error validating API key.');
            } finally {
                btnSaveAiConfig.disabled = false;
                btnSaveAiConfig.textContent = 'Save & Verify Key';
            }
        });
    }

    // ----------------------------------------------------------
    // FRESH ENTRY (RESET ARENA & TOPIC SELECTOR)
    // ----------------------------------------------------------
    const btnFreshEntry = document.getElementById('btn-fresh-entry');
    const btnCancelPrep = document.getElementById('btn-cancel-prep');
    const btnArenaFreshEntry = document.getElementById('btn-arena-fresh-entry');

    function performFreshEntry(focusCustom = true) {
        if (timer) timer.stop();
        if (speechManager) speechManager.stop();
        state.generatedQuestion = '';
        state.scratchpadText = '';
        if (scratchpad) scratchpad.value = '';
        if (answerTextarea) answerTextarea.value = '';
        updateAnswerMetrics();
        localStorage.removeItem('extempore_draft');
        switchView('launchpad');

        if (focusCustom) {
            selectTopicTab('custom');
            if (customTopicInput) {
                customTopicInput.value = '';
                customTopicInput.classList.add('custom-topic-highlight');
                customTopicInput.focus();
                setTimeout(() => {
                    customTopicInput.classList.remove('custom-topic-highlight');
                }, 2000);
            }
            presetChips.forEach(c => c.classList.remove('active'));
            showToast('✨ Ready for Fresh Entry! Type your topic or choose a headline below.', 'info');
        } else {
            selectTopicTab('rss');
            fetchHeadlines(state.selectedCategory);
            showToast('✨ Session reset to live breaking headlines!', 'info');
        }
    }

    if (btnFreshEntry) {
        btnFreshEntry.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            performFreshEntry(true);
        });
    }

    if (btnCancelPrep) {
        btnCancelPrep.addEventListener('click', () => {
            if (confirm('Discard this challenge and return to topic selection?')) {
                performFreshEntry(true);
            }
        });
    }

    if (btnArenaFreshEntry) {
        btnArenaFreshEntry.addEventListener('click', () => {
            if (confirm('Discard current speaking attempt and start fresh?')) {
                performFreshEntry(true);
            }
        });
    }

    // ----------------------------------------------------------
    // USER AUTHENTICATION (LOGIN / REGISTER / LOGOUT)
    // ----------------------------------------------------------
    const btnAuthTrigger = document.getElementById('btn-auth-trigger');
    const userProfileBadge = document.getElementById('user-profile-badge');
    const userDisplayName = document.getElementById('user-display-name');
    const btnLogout = document.getElementById('btn-logout');
    const authModal = document.getElementById('auth-modal');
    const btnCloseAuthModal = document.getElementById('btn-close-auth-modal');
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const authModalTitle = document.getElementById('auth-modal-title');
    const authErrorMsg = document.getElementById('auth-error-msg');
    const regErrorMsg = document.getElementById('reg-error-msg');

    async function checkCurrentUser() {
        try {
            const resp = await fetch('/api/auth/me');
            const data = await resp.json();
            if (data.authenticated && data.user) {
                if (btnAuthTrigger) btnAuthTrigger.style.display = 'none';
                if (userProfileBadge) {
                    userProfileBadge.style.display = 'flex';
                    userDisplayName.textContent = data.user.username;
                }
            } else {
                if (btnAuthTrigger) btnAuthTrigger.style.display = 'flex';
                if (userProfileBadge) userProfileBadge.style.display = 'none';
            }
        } catch (e) {}
    }

    if (btnAuthTrigger) {
        btnAuthTrigger.addEventListener('click', () => {
            authModal.classList.add('open');
            authErrorMsg.style.display = 'none';
            regErrorMsg.style.display = 'none';
        });
    }

    if (btnCloseAuthModal) {
        btnCloseAuthModal.addEventListener('click', () => {
            authModal.classList.remove('open');
        });
    }

    if (tabLogin && tabRegister) {
        tabLogin.addEventListener('click', () => {
            tabLogin.classList.add('active');
            tabRegister.classList.remove('active');
            formLogin.style.display = 'block';
            formRegister.style.display = 'none';
            authModalTitle.textContent = 'Candidate Sign In';
        });

        tabRegister.addEventListener('click', () => {
            tabRegister.classList.add('active');
            tabLogin.classList.remove('active');
            formLogin.style.display = 'none';
            formRegister.style.display = 'block';
            authModalTitle.textContent = 'Create Practice Account';
        });
    }

    if (formLogin) {
        formLogin.addEventListener('submit', async (e) => {
            e.preventDefault();
            const identifier = document.getElementById('login-identifier').value.trim();
            const password = document.getElementById('login-password').value;
            authErrorMsg.style.display = 'none';

            try {
                const resp = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ identifier, password })
                });
                const res = await resp.json();
                if (res.success) {
                    authModal.classList.remove('open');
                    checkCurrentUser();
                    loadAnalyticsData();
                    loadHistoryTable();
                } else {
                    authErrorMsg.textContent = res.message || 'Login failed.';
                    authErrorMsg.style.display = 'block';
                }
            } catch (err) {
                authErrorMsg.textContent = 'Connection error logging in.';
                authErrorMsg.style.display = 'block';
            }
        });
    }

    if (formRegister) {
        formRegister.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('reg-username').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value;
            regErrorMsg.style.display = 'none';

            try {
                const resp = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                const res = await resp.json();
                if (res.success) {
                    authModal.classList.remove('open');
                    checkCurrentUser();
                    loadAnalyticsData();
                    loadHistoryTable();
                } else {
                    regErrorMsg.textContent = res.message || 'Registration failed.';
                    regErrorMsg.style.display = 'block';
                }
            } catch (err) {
                regErrorMsg.textContent = 'Connection error registering account.';
                regErrorMsg.style.display = 'block';
            }
        });
    }

    if (btnLogout) {
        btnLogout.addEventListener('click', async () => {
            try {
                await fetch('/api/auth/logout', { method: 'POST' });
                checkCurrentUser();
                loadAnalyticsData();
                loadHistoryTable();
            } catch (e) {}
        });
    }

    // Dismiss modals when clicking backdrop
    [dbModal, sessionModal, aiModal, authModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('open');
                }
            });
        }
    });

    // Initial Load
    fetchHeadlines('polity');
    checkDbStatus();
    checkAiStatus();
    checkCurrentUser();
});
