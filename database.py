import os
import sqlite3
import pymysql
import pymysql.cursors
from config import Config

class DatabaseManager:
    def __init__(self):
        self.is_mysql = False
        self.last_error = None
        self.init_database()

    def get_mysql_conn(self, create_db=False):
        try:
            if create_db:
                conn = pymysql.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=3
                )
            else:
                conn = pymysql.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=3
                )
            return conn
        except Exception as e:
            self.last_error = str(e)
            return None

    def get_sqlite_conn(self):
        conn = sqlite3.connect(Config.SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Attempts to setup MySQL. If it fails, initializes SQLite mirror gracefully."""
        conn = self.get_mysql_conn(create_db=True)
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                conn.close()

                app_conn = self.get_mysql_conn(create_db=False)
                if app_conn:
                    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
                    if os.path.exists(schema_path):
                        with open(schema_path, 'r', encoding='utf-8') as f:
                            statements = f.read().split(';')
                            with app_conn.cursor() as cursor:
                                for stmt in statements:
                                    clean = stmt.strip()
                                    if clean:
                                        cursor.execute(clean)
                        app_conn.commit()
                    app_conn.close()
                    self.is_mysql = True
                    self.last_error = None
                    print("Successfully connected to MySQL and initialized extempore_db!")
                    return
            except Exception as e:
                self.last_error = f"MySQL setup error: {e}"
                print(self.last_error)

        if Config.ALLOW_SQLITE_FALLBACK:
            self.is_mysql = False
            self.init_sqlite_schema()
            print("Operating with Local DB (SQLite mirror). MySQL credentials can be configured in UI or .env anytime.")

    def init_sqlite_schema(self):
        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            icon TEXT DEFAULT '📌',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS headlines_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            headline TEXT NOT NULL,
            source_name TEXT,
            source_url TEXT,
            published_date TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS practice_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NULL,
            category_name TEXT NOT NULL,
            headline TEXT NOT NULL,
            source_name TEXT,
            question TEXT NOT NULL,
            prep_time_seconds INTEGER NOT NULL DEFAULT 60,
            answer_time_seconds INTEGER NOT NULL DEFAULT 300,
            time_taken_seconds INTEGER NOT NULL DEFAULT 0,
            user_answer TEXT NOT NULL,
            word_count INTEGER DEFAULT 0,
            input_mode TEXT DEFAULT 'text',
            scratchpad_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            score_factual INTEGER NOT NULL,
            score_relevance INTEGER NOT NULL,
            score_structure INTEGER NOT NULL,
            score_depth INTEGER NOT NULL,
            score_time INTEGER NOT NULL,
            total_score INTEGER NOT NULL,
            factual_feedback TEXT,
            relevance_feedback TEXT,
            structure_feedback TEXT,
            depth_feedback TEXT,
            time_feedback TEXT,
            overall_feedback TEXT,
            model_answer_structure TEXT,
            ai_evaluator_type TEXT DEFAULT 'gemini-or-rubric',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        INSERT OR IGNORE INTO categories (id, name, slug, icon, description) VALUES
        (1, 'National & Polity (UPSC)', 'polity', '🇮🇳', 'Governance, constitutional amendments, public policy, and national developments'),
        (2, 'International Relations', 'world', '🌍', 'Geopolitics, multilateral summits, treaties, and global diplomacy'),
        (3, 'Tech, AI & Cybersecurity', 'tech', '💻', 'Artificial intelligence, cybersecurity breaches, digital data sovereignty, and space tech'),
        (4, 'Economy & Sustainable Growth', 'economy', '📈', 'Fiscal policy, inflation, climate economics, infrastructure, and markets'),
        (5, 'Sports, Society & Culture', 'sports', '⚽', 'Major sporting events, social ethics, cultural heritage, and institutional reforms'),
        (6, 'General / Live News Mix', 'general', '🎲', 'Eclectic top breaking headlines for spontaneous debate');
        """)
        conn.commit()
        conn.close()

    def get_status(self):
        return {
            'is_mysql': self.is_mysql,
            'db_type': 'MySQL 8.0' if self.is_mysql else 'SQLite (Local Fallback)',
            'host': Config.DB_HOST if self.is_mysql else 'Local File',
            'database': Config.DB_NAME if self.is_mysql else Config.SQLITE_PATH,
            'user': Config.DB_USER if self.is_mysql else 'system',
            'last_error': self.last_error
        }

    def test_and_update_credentials(self, host, port, user, password, db_name):
        try:
            port = int(port)
            conn = pymysql.connect(
                host=host, port=port, user=user, password=password,
                charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, connect_timeout=3
            )
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.close()

            Config.DB_HOST = host
            Config.DB_PORT = port
            Config.DB_USER = user
            Config.DB_PASSWORD = password
            Config.DB_NAME = db_name

            env_path = os.path.join(os.path.dirname(__file__), '.env')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(f"DB_HOST={host}\nDB_PORT={port}\nDB_USER={user}\nDB_PASSWORD={password}\nDB_NAME={db_name}\nALLOW_SQLITE_FALLBACK=true\n")

            self.init_database()
            return {'success': True, 'message': 'Successfully connected to MySQL and updated configuration!'}
        except Exception as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}

    def create_user(self, username, email, password_hash):
        if self.is_mysql:
            conn = self.get_mysql_conn()
            if not conn:
                return {'success': False, 'message': 'Database not connected'}
            try:
                with conn.cursor() as cursor:
                    sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (username, email, password_hash))
                    user_id = cursor.lastrowid
                conn.commit()
                return {'success': True, 'user_id': user_id}
            except Exception as e:
                return {'success': False, 'message': str(e)}
            finally:
                conn.close()
        else:
            conn = self.get_sqlite_conn()
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)"
                cursor.execute(sql, (username, email, password_hash))
                user_id = cursor.lastrowid
                conn.commit()
                return {'success': True, 'user_id': user_id}
            except Exception as e:
                return {'success': False, 'message': str(e)}
            finally:
                conn.close()

    def get_user_by_identifier(self, identifier):
        query = "SELECT * FROM users WHERE username = %s OR email = %s" if self.is_mysql else "SELECT * FROM users WHERE username = ? OR email = ?"
        if self.is_mysql:
            conn = self.get_mysql_conn()
            if not conn: return None
            with conn.cursor() as cursor:
                cursor.execute(query, (identifier, identifier))
                row = cursor.fetchone()
            conn.close()
            return row
        else:
            conn = self.get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(query, (identifier, identifier))
            res = cursor.fetchone()
            conn.close()
            return dict(res) if res else None

    def get_user_by_id(self, user_id):
        query = "SELECT id, username, email, created_at FROM users WHERE id = %s" if self.is_mysql else "SELECT id, username, email, created_at FROM users WHERE id = ?"
        if self.is_mysql:
            conn = self.get_mysql_conn()
            if not conn: return None
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
            conn.close()
            return row
        else:
            conn = self.get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(query, (user_id,))
            res = cursor.fetchone()
            conn.close()
            return dict(res) if res else None

    def save_practice_session(self, category_name, headline, source_name, question,
                              prep_time, answer_time, time_taken, user_answer, word_count, input_mode, scratchpad, user_id=None):
        if self.is_mysql:
            conn = self.get_mysql_conn()
            with conn.cursor() as cursor:
                sql = """INSERT INTO practice_sessions 
                         (user_id, category_name, headline, source_name, question, prep_time_seconds, 
                          answer_time_seconds, time_taken_seconds, user_answer, word_count, input_mode, scratchpad_notes)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (user_id, category_name, headline, source_name, question, prep_time, 
                                     answer_time, time_taken, user_answer, word_count, input_mode, scratchpad))
                session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id
        else:
            conn = self.get_sqlite_conn()
            cursor = conn.cursor()
            sql = """INSERT INTO practice_sessions 
                     (user_id, category_name, headline, source_name, question, prep_time_seconds, 
                      answer_time_seconds, time_taken_seconds, user_answer, word_count, input_mode, scratchpad_notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, (user_id, category_name, headline, source_name, question, prep_time, 
                                 answer_time, time_taken, user_answer, word_count, input_mode, scratchpad))
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return session_id

    def save_evaluation(self, session_id, score_factual, score_relevance, score_structure,
                        score_depth, score_time, total_score, factual_fb, relevance_fb,
                        structure_fb, depth_fb, time_fb, overall_fb, model_structure, evaluator_type):
        if self.is_mysql:
            conn = self.get_mysql_conn()
            with conn.cursor() as cursor:
                sql = """INSERT INTO evaluations 
                         (session_id, score_factual, score_relevance, score_structure, score_depth, score_time, total_score,
                          factual_feedback, relevance_feedback, structure_feedback, depth_feedback, time_feedback,
                          overall_feedback, model_answer_structure, ai_evaluator_type)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (session_id, score_factual, score_relevance, score_structure, score_depth, score_time, total_score,
                                     factual_fb, relevance_fb, structure_fb, depth_fb, time_fb, overall_fb, model_structure, evaluator_type))
            conn.commit()
            conn.close()
        else:
            conn = self.get_sqlite_conn()
            cursor = conn.cursor()
            sql = """INSERT INTO evaluations 
                     (session_id, score_factual, score_relevance, score_structure, score_depth, score_time, total_score,
                      factual_feedback, relevance_feedback, structure_feedback, depth_feedback, time_feedback,
                      overall_feedback, model_answer_structure, ai_evaluator_type)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, (session_id, score_factual, score_relevance, score_structure, score_depth, score_time, total_score,
                                 factual_fb, relevance_fb, structure_fb, depth_fb, time_fb, overall_fb, model_structure, evaluator_type))
            conn.commit()
            conn.close()

    def get_history(self, limit=50, user_id=None):
        where_clause_mysql = "WHERE s.user_id = %s" if user_id else ""
        where_clause_sqlite = "WHERE s.user_id = ?" if user_id else ""
        params = (user_id, limit) if user_id else (limit,)

        query = f"""
            SELECT s.id, s.category_name, s.headline, s.question, s.word_count, s.time_taken_seconds,
                   s.created_at, e.total_score, e.score_factual, e.score_relevance, e.score_structure,
                   e.score_depth, e.score_time, e.overall_feedback
            FROM practice_sessions s
            LEFT JOIN evaluations e ON s.id = e.session_id
            {where_clause_mysql}
            ORDER BY s.created_at DESC
            LIMIT %s
        """ if self.is_mysql else f"""
            SELECT s.id, s.category_name, s.headline, s.question, s.word_count, s.time_taken_seconds,
                   s.created_at, e.total_score, e.score_factual, e.score_relevance, e.score_structure,
                   e.score_depth, e.score_time, e.overall_feedback
            FROM practice_sessions s
            LEFT JOIN evaluations e ON s.id = e.session_id
            {where_clause_sqlite}
            ORDER BY s.created_at DESC
            LIMIT ?
        """
        if self.is_mysql:
            conn = self.get_mysql_conn()
            if not conn: return []
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
            conn.close()
            return rows
        else:
            conn = self.get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = [dict(ix) for ix in cursor.fetchall()]
            conn.close()
            return rows

    def get_session_detail(self, session_id):
        query = """
            SELECT s.*, e.score_factual, e.score_relevance, e.score_structure, e.score_depth, e.score_time,
                   e.total_score, e.factual_feedback, e.relevance_feedback, e.structure_feedback,
                   e.depth_feedback, e.time_feedback, e.overall_feedback, e.model_answer_structure,
                   e.ai_evaluator_type
            FROM practice_sessions s
            LEFT JOIN evaluations e ON s.id = e.session_id
            WHERE s.id = %s
        """ if self.is_mysql else """
            SELECT s.*, e.score_factual, e.score_relevance, e.score_structure, e.score_depth, e.score_time,
                   e.total_score, e.factual_feedback, e.relevance_feedback, e.structure_feedback,
                   e.depth_feedback, e.time_feedback, e.overall_feedback, e.model_answer_structure,
                   e.ai_evaluator_type
            FROM practice_sessions s
            LEFT JOIN evaluations e ON s.id = e.session_id
            WHERE s.id = ?
        """
        if self.is_mysql:
            conn = self.get_mysql_conn()
            with conn.cursor() as cursor:
                cursor.execute(query, (session_id,))
                row = cursor.fetchone()
            conn.close()
            return row
        else:
            conn = self.get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(query, (session_id,))
            res = cursor.fetchone()
            conn.close()
            return dict(res) if res else None

    def get_analytics(self, user_id=None):
        history = self.get_history(limit=100, user_id=user_id)
        total_sessions = len(history)
        if total_sessions == 0:
            return {
                'total_sessions': 0,
                'average_score': 0,
                'total_words': 0,
                'streak_days': 0,
                'category_breakdown': {},
                'rubric_averages': {'factual': 0, 'relevance': 0, 'structure': 0, 'depth': 0, 'time': 0},
                'timeline': []
            }

        scores = [h['total_score'] for h in history if h.get('total_score') is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0
        total_words = sum(h.get('word_count') or 0 for h in history)

        rubric_sums = {'factual': 0, 'relevance': 0, 'structure': 0, 'depth': 0, 'time': 0}
        rubric_count = 0
        cat_counts = {}

        for h in history:
            cat = h.get('category_name') or 'General'
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            if h.get('total_score') is not None:
                rubric_sums['factual'] += h.get('score_factual') or 0
                rubric_sums['relevance'] += h.get('score_relevance') or 0
                rubric_sums['structure'] += h.get('score_structure') or 0
                rubric_sums['depth'] += h.get('score_depth') or 0
                rubric_sums['time'] += h.get('score_time') or 0
                rubric_count += 1

        rubric_averages = {
            k: round(v / rubric_count, 1) if rubric_count else 0
            for k, v in rubric_sums.items()
        }

        timeline = [
            {
                'id': h['id'],
                'date': str(h.get('created_at', ''))[:10],
                'score': h.get('total_score', 0),
                'category': h.get('category_name', '')
            }
            for h in reversed(history[:15])
        ]

        return {
            'total_sessions': total_sessions,
            'average_score': avg_score,
            'total_words': total_words,
            'streak_days': min(total_sessions, 5),
            'category_breakdown': cat_counts,
            'rubric_averages': rubric_averages,
            'timeline': timeline
        }

db_manager = DatabaseManager()
