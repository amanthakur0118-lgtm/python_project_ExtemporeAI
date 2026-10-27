from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import os
from config import Config
from database import db_manager
import news_service
import ai_service
import quiz_service

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.svg', mimetype='image/svg+xml')

@app.route('/')
def index():
    db_status = db_manager.get_status()
    return render_template('index.html', db_status=db_status)

# ----------------------------------------------------------
# AUTHENTICATION API (LOGIN / SIGN UP / LOGOUT)
# ----------------------------------------------------------
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters.'}), 400
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters.'}), 400

    existing_user = db_manager.get_user_by_identifier(username)
    if existing_user:
        return jsonify({'success': False, 'message': 'Username is already taken.'}), 400
    if email:
        existing_email = db_manager.get_user_by_identifier(email)
        if existing_email:
            return jsonify({'success': False, 'message': 'Email is already registered.'}), 400

    password_hash = generate_password_hash(password)
    res = db_manager.create_user(username, email or None, password_hash)
    if res.get('success'):
        user_id = res['user_id']
        session['user_id'] = user_id
        session['username'] = username
        db_manager.claim_guest_sessions(user_id)
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'user': {'id': user_id, 'username': username, 'email': email}
        })
    return jsonify({'success': False, 'message': res.get('message', 'Registration failed.')}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'success': False, 'message': 'Please provide username/email and password.'}), 400

    user = db_manager.get_user_by_identifier(identifier)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    if not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    db_manager.claim_guest_sessions(user['id'])
    return jsonify({
        'success': True,
        'message': f"Welcome back, {user['username']}!",
        'user': {'id': user['id'], 'username': user['username'], 'email': user.get('email')}
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False, 'user': None})
    user = db_manager.get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'authenticated': False, 'user': None})
    return jsonify({'authenticated': True, 'user': user})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = [
        {"id": 1, "name": "National & Polity (UPSC)", "slug": "polity", "icon": "🇮🇳", "description": "Governance, constitutional law, public administration, and national policies"},
        {"id": 2, "name": "International Relations", "slug": "world", "icon": "🌍", "description": "Geopolitics, global multilateralism, foreign treaties, and strategic diplomacy"},
        {"id": 3, "name": "Tech, AI & Cybersecurity", "slug": "tech", "icon": "💻", "description": "Cyber resilience, AI ethics, cloud sovereignty, and disruptive tech"},
        {"id": 4, "name": "Economy & Development", "slug": "economy", "icon": "📈", "description": "Macroeconomics, budget, fiscal reforms, trade, and climate financing"},
        {"id": 5, "name": "Sports & Society", "slug": "sports", "icon": "⚽", "description": "Sports governance, ethical debates, institutional reforms, and youth affairs"},
        {"id": 6, "name": "General / Live Mix", "slug": "general", "icon": "🎲", "description": "Fast-paced breaking news mix across diverse contemporary themes"}
    ]
    return jsonify({'categories': categories})

@app.route('/api/news/<category_slug>', methods=['GET'])
def get_news(category_slug):
    max_items = request.args.get('limit', 8, type=int)
    headlines = news_service.fetch_live_headlines(category=category_slug, max_items=max_items)
    return jsonify({'category': category_slug, 'headlines': headlines})

@app.route('/api/generate-question', methods=['POST'])
def generate_question():
    data = request.get_json() or {}
    headline = data.get('headline', '').strip()
    category = data.get('category', 'general').strip()
    
    if not headline:
        # Pick a fresh random headline if none provided
        random_topic = news_service.get_random_topic(category)
        headline = random_topic['headline']
        source_name = random_topic['source']
    else:
        source_name = data.get('source', 'Live News')

    question = ai_service.generate_extempore_question(headline, category)
    return jsonify({
        'headline': headline,
        'source': source_name,
        'category': category,
        'question': question
    })

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json() or {}
    
    question = data.get('question', '').strip()
    headline = data.get('headline', '').strip()
    category_name = data.get('category_name', 'General')
    source_name = data.get('source_name', 'News')
    user_answer = data.get('user_answer', '').strip()
    prep_time = int(data.get('prep_time', 60))
    answer_time = int(data.get('answer_time', 300))
    time_taken = int(data.get('time_taken', 300))
    input_mode = data.get('input_mode', 'text')
    scratchpad = data.get('scratchpad', '')
    
    if not user_answer:
        return jsonify({'error': 'Answer cannot be empty.'}), 400

    word_count = len(user_answer.split())
    
    # 1. Run AI Rubric Evaluation
    eval_result = ai_service.evaluate_answer_rubric(question, user_answer, time_taken_seconds=time_taken)
    
    # 2. Persist in MySQL Database
    user_id = session.get('user_id')
    try:
        session_id = db_manager.save_practice_session(
            category_name=category_name,
            headline=headline,
            source_name=source_name,
            question=question,
            prep_time=prep_time,
            answer_time=answer_time,
            time_taken=time_taken,
            user_answer=user_answer,
            word_count=word_count,
            input_mode=input_mode,
            scratchpad=scratchpad,
            user_id=user_id
        )
        
        db_manager.save_evaluation(
            session_id=session_id,
            score_factual=eval_result['score_factual'],
            score_relevance=eval_result['score_relevance'],
            score_structure=eval_result['score_structure'],
            score_depth=eval_result['score_depth'],
            score_time=eval_result['score_time'],
            total_score=eval_result['total_score'],
            factual_fb=eval_result['factual_feedback'],
            relevance_fb=eval_result['relevance_feedback'],
            structure_fb=eval_result['structure_feedback'],
            depth_fb=eval_result['depth_feedback'],
            time_fb=eval_result['time_feedback'],
            overall_fb=eval_result['overall_feedback'],
            model_structure=eval_result['model_answer_structure'],
            evaluator_type=eval_result['ai_evaluator_type']
        )
    except Exception as e:
        print(f"Database save notice: {e}")
        session_id = 1

    return jsonify({
        'success': True,
        'session_id': session_id,
        'word_count': word_count,
        'evaluation': eval_result
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    limit = request.args.get('limit', 50, type=int)
    user_id = session.get('user_id')
    history = db_manager.get_history(limit=limit, user_id=user_id)
    return jsonify({'history': history})

@app.route('/api/session/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = db_manager.get_session_detail(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify({'session': session})

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    user_id = session.get('user_id')
    analytics = db_manager.get_analytics(user_id=user_id)
    return jsonify(analytics)

@app.route('/api/db-status', methods=['GET'])
def get_db_status():
    return jsonify(db_manager.get_status())

@app.route('/api/db-config', methods=['POST'])
def update_db_config():
    data = request.get_json() or {}
    host = data.get('host', 'localhost')
    port = data.get('port', 3306)
    user = data.get('user', 'root')
    password = data.get('password', '')
    db_name = data.get('db_name', 'extempore_db')
    
    result = db_manager.test_and_update_credentials(host, port, user, password, db_name)
    return jsonify(result)

@app.route('/api/ai-status', methods=['GET'])
def get_ai_status():
    has_gemini = bool(Config.GEMINI_API_KEY)
    return jsonify({
        'has_gemini': has_gemini,
        'model_name': 'Gemini 2.5 Flash' if has_gemini else 'Strict Rubric Engine (UPSC Standard)',
        'description': 'Direct LLM reasoning with Google AI Studio' if has_gemini else 'Strict multi-metric quality guard (Offline)'
    })

@app.route('/api/ai-config', methods=['POST'])
def update_ai_config():
    data = request.get_json() or {}
    api_key = data.get('api_key', '').strip()
    if not api_key:
        Config.GEMINI_API_KEY = ''
        return jsonify({'success': True, 'message': 'Reverted to Strict Rubric Engine (Offline).'})
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Respond with the word OK'
        )
        if resp and resp.text:
            Config.GEMINI_API_KEY = api_key
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            key_set = False
            for i, line in enumerate(lines):
                if line.startswith('GEMINI_API_KEY='):
                    lines[i] = f'GEMINI_API_KEY={api_key}\n'
                    key_set = True
                    break
            if not key_set:
                lines.append(f'GEMINI_API_KEY={api_key}\n')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return jsonify({'success': True, 'message': 'Gemini API key successfully verified and activated!'})
        else:
            return jsonify({'success': False, 'message': 'API key did not return a valid response.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'API key validation failed: {str(e)}'})

# ----------------------------------------------------------
# DAILY CURRENT AFFAIRS QUIZ API
# ----------------------------------------------------------
@app.route('/api/quiz', methods=['GET'])
def get_quiz():
    category = request.args.get('category', 'polity').strip().lower()
    questions = quiz_service.generate_quiz_for_category(category, count=5)
    return jsonify({
        'category': category,
        'total_questions': len(questions),
        'questions': questions
    })

@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz():
    data = request.get_json() or {}
    category = data.get('category', 'General')
    submitted_answers = data.get('answers', {})
    original_questions = data.get('questions', [])
    time_taken = int(data.get('time_taken', 0))

    if not original_questions:
        return jsonify({'error': 'No questions submitted for grading.'}), 400

    grade_result = quiz_service.grade_quiz_submission(submitted_answers, original_questions)
    
    # Save to database
    user_id = session.get('user_id')
    db_manager.save_quiz_result(
        user_id=user_id,
        category_name=category,
        score=grade_result['score'],
        total_questions=grade_result['total_questions'],
        time_taken_seconds=time_taken
    )

    return jsonify(grade_result)

@app.route('/api/quiz/history', methods=['GET'])
def get_quiz_history():
    user_id = session.get('user_id')
    history = db_manager.get_quiz_history(user_id=user_id, limit=15)
    return jsonify({'history': history})

if __name__ == '__main__':
    print(f"Extempore App running on http://127.0.0.1:5000")
    print(f"Database: {db_manager.get_status()['db_type']}")
    app.run(host='0.0.0.0', port=5000, debug=True)

