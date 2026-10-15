import json
import re
from config import Config

TASK1_PROMPT = """You are acting as an AI examiner for an extempore/current-affairs practice app.

TASK 1 — QUESTION GENERATION:
Given the following news headline/summary, generate ONE clear, thought-provoking extempore-style question a student could answer in 5 minutes. The question should require opinion + analysis, not just a one-line factual answer.

Headline: "{headline}"

Return only the question, nothing else."""

TASK2_PROMPT = """You are an impartial, strict examiner evaluating an impromptu extempore speaking answer for a competitive exam / UPSC interview board.

Question: "{question}"
Student's Answer: "{answer}"
Time Spent: {time_spent} seconds (out of 300 seconds allotted)

CRITICAL GRADING INSTRUCTIONS:
1. If the student's answer is rubbish, nonsensical gibberish (e.g. random letters, keyboard smashing, unrelated words like "banana pizza haha"), award 0 to 1 for Factual, Relevance, Structure, Depth, and Time. Total score must be between 1 and 5 out of 50!
2. If the answer is off-topic (e.g., talks about movies or cricket when asked about economics/governance), award at most 1/10 for Relevance, 2/10 for Factual, and 1/10 for Depth. Total score must be below 15/50.
3. If the answer is too short (less than 40 words), award maximum 2-3 for Time Discipline, Structure, and Depth.
4. If the answer merely repeats or paraphrases the question without providing an actual opinion, arguments, or solution, award maximum 1/10 for Relevance and Depth.
5. Only award high marks (35-50) to well-structured, multi-dimensional answers with clear arguments and a constructive way forward.
6. Provide concrete reasons citing specific flaws or strong points in the answer.

Score each category out of 10, then give a total out of 50:
- Factual Accuracy (10)
- Relevance (10)
- Structure & Clarity (10)
- Depth of Analysis (10)
- Time Discipline (10)

Respond ONLY with valid JSON with this exact structure:
{{
  "score_factual": 0,
  "factual_feedback": "Concrete reason...",
  "score_relevance": 0,
  "relevance_feedback": "Concrete reason...",
  "score_structure": 0,
  "structure_feedback": "Concrete reason...",
  "score_depth": 0,
  "depth_feedback": "Concrete reason...",
  "score_time": 0,
  "time_feedback": "Concrete reason...",
  "total_score": 0,
  "overall_feedback": "Honest, constructive evaluation of the performance.",
  "model_answer_structure": "A suggested 3-stage outline of how a top candidate would frame this extempore."
}}"""

COMMON_ENGLISH_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he',
    'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or',
    'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about',
    'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
    'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two',
    'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give',
    'day', 'most', 'us', 'is', 'are', 'was', 'were', 'has', 'had', 'been', 'should', 'must', 'need', 'issue',
    'policy', 'reform', 'government', 'public', 'india', 'state', 'country', 'world', 'society', 'growth'
}

def call_gemini_api(prompt, as_json=False):
    """Attempts to call Gemini API if key is available."""
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        if response and response.text:
            text = response.text.strip()
            if as_json:
                text = re.sub(r'^```json\s*', '', text)
                text = re.sub(r'```$', '', text).strip()
                return json.loads(text)
            return text
    except Exception as e:
        print(f"Gemini API call notice: {e}")
    return None

def generate_extempore_question(headline, category='general'):
    """Generates an extempore question from a live headline."""
    gemini_resp = call_gemini_api(TASK1_PROMPT.format(headline=headline))
    if gemini_resp and len(gemini_resp) > 20:
        return gemini_resp.strip('"\n ')

    clean = headline.rstrip('. ')
    category = category.lower()
    
    if category == 'polity':
        templates = [
            f"Critically analyze the democratic and institutional implications of '{clean}'. How can India balance executive efficiency with constitutional safeguards?",
            f"In light of '{clean}', discuss the evolving role of public policy and accountability in modern governance. What reforms are urgent?"
        ]
    elif category == 'tech':
        templates = [
            f"As highlighted by '{clean}', how should policymakers balance technological innovation against cybersecurity, digital sovereignty, and ethical risks?",
            f"Critically assess the societal and economic ramifications of '{clean}'. What governance frameworks are necessary to safeguard user trust?"
        ]
    elif category == 'economy':
        templates = [
            f"Evaluate the structural economic impacts of '{clean}'. How should developing nations navigate macroeconomic headwinds while ensuring inclusive growth?",
            f"In the context of '{clean}', critically examine the trade-offs between fiscal discipline and social sector investments."
        ]
    elif category == 'world':
        templates = [
            f"In the backdrop of '{clean}', critically assess the shifting dynamics of global multilateralism and India's strategic autonomy.",
            f"How does '{clean}' impact international order, supply chain resilience, and diplomatic equilibrium in the Global South?"
        ]
    elif category == 'sports':
        templates = [
            f"Reflecting on '{clean}', what institutional reforms and ethical standards are essential to elevate sports governance and athlete welfare globally?",
            f"In view of '{clean}', discuss how sports diplomacy and grassroots infrastructure can drive national youth empowerment."
        ]
    else:
        templates = [
            f"In light of the recent development regarding '{clean}', critically evaluate the underlying challenges and outline a balanced, actionable roadmap.",
            f"Analyze the socio-economic and ethical ramifications of '{clean}'. What key stakeholders must intervene to ensure long-term sustainability?"
        ]

    import random
    return random.choice(templates)

def evaluate_answer_rubric(question, user_answer, time_taken_seconds=300):
    """Evaluates the student answer using strict rubric standards."""
    time_taken_seconds = max(10, int(time_taken_seconds))
    cleaned_answer = user_answer.strip()
    words = cleaned_answer.split()
    word_count = len(words)
    text_lower = cleaned_answer.lower()
    
    # 1. Try Live Gemini LLM if key is present
    gemini_eval = call_gemini_api(
        TASK2_PROMPT.format(question=question, answer=cleaned_answer, time_spent=time_taken_seconds),
        as_json=True
    )
    if gemini_eval and 'total_score' in gemini_eval:
        gemini_eval['ai_evaluator_type'] = 'Gemini 2.5 Flash (Strict LLM)'
        # Ensure scores are within bounds
        for k in ['score_factual', 'score_relevance', 'score_structure', 'score_depth', 'score_time']:
            gemini_eval[k] = max(0, min(10, int(gemini_eval.get(k, 0))))
        gemini_eval['total_score'] = sum(gemini_eval[k] for k in ['score_factual', 'score_relevance', 'score_structure', 'score_depth', 'score_time'])
        return gemini_eval

    # 2. Strict Deterministic Algorithmic Rubric Engine (Fallback)
    
    # Check A: Character repetition / Keyboard smash (e.g., 'asdfasdf', 'aaaa')
    repeated_chars = len(re.findall(r'(.)\1{3,}', cleaned_answer))
    unique_words = len(set(w.lower() for w in words))
    unique_ratio = unique_words / max(1, word_count)
    
    # Count recognized English words
    english_word_count = sum(1 for w in words if re.sub(r'[^a-zA-Z]', '', w.lower()) in COMMON_ENGLISH_WORDS)
    english_ratio = english_word_count / max(1, word_count)
    
    is_gibberish = (
        (word_count < 12 and english_ratio < 0.4) or
        (unique_ratio < 0.35 and word_count >= 10) or
        (english_ratio < 0.20 and word_count >= 5) or
        repeated_chars >= 2
    )

    # Check B: Question echo / parrot
    q_words_all = re.findall(r'\b[a-zA-Z]{3,}\b', question.lower())
    q_words_set = set(q_words_all)
    stopwords = {
        'the', 'and', 'for', 'are', 'all', 'can', 'has', 'its', 'our', 'how', 'who', 'why', 'what',
        'when', 'where', 'which', 'that', 'this', 'with', 'from', 'have', 'been', 'will', 'should',
        'would', 'could', 'about', 'light', 'recent', 'critically', 'discuss', 'analyze', 'examine',
        'impact', 'implications', 'reforms', 'urgent', 'development', 'role', 'such', 'into', 'some',
        'more', 'also', 'over', 'than', 'them', 'then', 'they', 'were', 'your', 'like', 'just', 'does',
        'evaluate', 'outline', 'assess', 'between', 'against', 'during', 'under', 'through', 'was',
        'any', 'not', 'but', 'well', 'way', 'even', 'new', 'want', 'because', 'these', 'give', 'day',
        'most', 'need', 'issue', 'policy', 'state', 'country', 'world', 'society'
    }
    q_keywords = q_words_set - stopwords
    ans_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', text_lower))
    overlap = len(q_keywords.intersection(ans_words))
    
    is_question_echo = False
    if word_count > 0:
        question_matched = sum(1 for w in words if w.lower() in q_words_set)
        if question_matched / word_count >= 0.75 and word_count <= len(question.split()) + 8:
            is_question_echo = True

    # Check C: Off-Topic (No overlap with core subject keywords)
    is_off_topic = (overlap == 0 and word_count >= 10 and not is_gibberish)

    # ----------------------------------------------------
    # SCENARIO 1: PURE GIBBERISH / NONSENSE / EMPTY
    # ----------------------------------------------------
    if is_gibberish or word_count < 8:
        score_f = 0
        score_r = 0
        score_s = 1
        score_d = 0
        score_t = 1
        total = score_f + score_r + score_s + score_d + score_t
        return {
            'score_factual': score_f,
            'factual_feedback': "Zero factual credibility: The submission consists of random, incoherent, or placeholder text.",
            'score_relevance': score_r,
            'relevance_feedback': "Completely off-target: Failed to address the extempore prompt or present any relevant statement.",
            'score_structure': score_s,
            'structure_feedback': "Unstructured: Lacks intelligible sentence formation, syntax, or paragraph organization.",
            'score_depth': score_d,
            'depth_feedback': "Zero analytical depth: No arguments, viewpoints, or reasoning were articulated.",
            'score_time': score_t,
            'time_feedback': f"Severely insufficient: Generated only {word_count} words in {time_taken_seconds} seconds.",
            'total_score': total,
            'overall_feedback': "❌ Disqualified / Non-Response: The answer does not meet minimum standards of speech or composition. In an extempore round or UPSC interview, this would be graded as an immediate fail. Focus on delivering genuine, coherent arguments directly addressing the topic.",
            'model_answer_structure': "1. Context (1m): Define the core issue.\n2. Analysis (2.5m): Present arguments and counter-arguments.\n3. Solutions (1.5m): Propose a practical Way Forward.",
            'ai_evaluator_type': 'Strict Rubric Examiner (Quality Guard)'
        }

    # ----------------------------------------------------
    # SCENARIO 2: QUESTION ECHO (COPY-PASTED PROMPT)
    # ----------------------------------------------------
    if is_question_echo:
        score_f = 2
        score_r = 2
        score_s = 2
        score_d = 1
        score_t = 2
        total = score_f + score_r + score_s + score_d + score_t
        return {
            'score_factual': score_f,
            'factual_feedback': "The response merely mirrors the prompt without introducing independent facts or empirical knowledge.",
            'score_relevance': score_r,
            'relevance_feedback': "Tautological: You restated the question rather than answering it with an opinion and analysis.",
            'score_structure': score_s,
            'structure_feedback': "No extempore flow: Missing the standard tripartite structure (Introduction, Arguments, Conclusion).",
            'score_depth': score_d,
            'depth_feedback': "Zero depth: Did not provide any reasoning, evidence, or multi-dimensional viewpoints.",
            'score_time': score_t,
            'time_feedback': f"Unacceptably brief: Only {word_count} words provided for a 5-minute timed challenge.",
            'total_score': total,
            'overall_feedback': "⚠️ Circular Evasion: Copying or rephrasing the question does not earn credit in extempore rounds. An examiner looks for your spontaneous perspective, structured arguments, and recommendations.",
            'model_answer_structure': "1. Stance (1m): State your viewpoint.\n2. Dimensions (2.5m): Assess social, economic, and institutional aspects.\n3. Roadmap (1.5m): Specific actionable recommendations.",
            'ai_evaluator_type': 'Strict Rubric Examiner (Quality Guard)'
        }

    # ----------------------------------------------------
    # SCENARIO 3: COMPLETELY OFF-TOPIC
    # ----------------------------------------------------
    if is_off_topic:
        score_f = 2
        score_r = 1
        score_s = 3 if '\n' in cleaned_answer or word_count > 40 else 2
        score_d = 1
        score_t = 3 if word_count >= 50 else 2
        total = score_f + score_r + score_s + score_d + score_t
        return {
            'score_factual': score_f,
            'factual_feedback': "Irrelevant claims: Whatever claims were made do not pertain to the assigned current affairs topic.",
            'score_relevance': score_r,
            'relevance_feedback': "Severe topical divergence: You discussed an unrelated subject with 0% overlap with the core question.",
            'score_structure': score_s,
            'structure_feedback': "Grammar may be present, but the rhetorical flow is invalid because the prompt was ignored.",
            'score_depth': score_d,
            'depth_feedback': "Zero topic depth: No analysis of the designated policy, event, or problem statement.",
            'score_time': score_t,
            'time_feedback': f"Pacing wasted on off-topic monologue ({word_count} words).",
            'total_score': total,
            'overall_feedback': "⚠️ Off-Topic Submission: In UPSC and debate tournaments, staying strictly on-topic is mandatory. Irrelevant content is heavily penalized, regardless of grammatical fluency. Always anchor your speech around the specific prompt.",
            'model_answer_structure': "1. Context (1m): Define the specific assigned development.\n2. Core Analysis (2.5m): Address the exact implications asked.\n3. Conclusion (1.5m): Synthesize with a forward-looking roadmap.",
            'ai_evaluator_type': 'Strict Rubric Examiner (Quality Guard)'
        }

    # ----------------------------------------------------
    # SCENARIO 4: SEVERELY BRIEF (< 40 WORDS)
    # ----------------------------------------------------
    if word_count < 40:
        score_f = 3
        score_r = min(5, 2 + overlap)
        score_s = 2
        score_d = 2
        score_t = 2
        total = score_f + score_r + score_s + score_d + score_t
        return {
            'score_factual': score_f,
            'factual_feedback': "Very sparse factual substance: Only touched the surface without evidence or data.",
            'score_relevance': score_r,
            'relevance_feedback': f"Attempted the topic ({overlap} keyword matches), but terminated prematurely before developing an argument.",
            'score_structure': score_s,
            'structure_feedback': "Fragmentary: Missing a proper body and conclusion.",
            'score_depth': score_d,
            'depth_feedback': "Superficial: States a conclusion without showing the analytical steps to reach it.",
            'score_time': score_t,
            'time_feedback': f"Severely deficient duration: {word_count} words leaves over 4 minutes of dead air in a 5-minute round.",
            'total_score': total,
            'overall_feedback': "⏱️ Underdeveloped Extempore: You must sustain your speech for the full duration. Aim for at least 250–400 words to give a comprehensive, credible response.",
            'model_answer_structure': "1. Hook & Context (1m)\n2. Stakeholder Perspectives (2.5m)\n3. Concrete Way Forward (1.5m)",
            'ai_evaluator_type': 'Strict Rubric Examiner (Quality Guard)'
        }

    # ----------------------------------------------------
    # SCENARIO 5: GENUINE ATTEMPT (GRANULAR EVALUATION)
    # ----------------------------------------------------
    
    # 1. Factual Accuracy (0 - 10)
    domain_terms = ['act', 'policy', 'article', 'system', 'data', 'percent', 'treaty', 'committee', 
                    'court', 'institution', 'judiciary', 'parliament', 'constitution', 'amendment', 
                    'ruling', 'framework', 'statutory', 'infrastructure', 'governance', 'inflation',
                    'economy', 'gdp', 'bilateral', 'security', 'cyber', 'digital', 'sovereignty']
    found_terms = [t for t in domain_terms if t in text_lower]
    
    score_factual = 4
    if len(found_terms) >= 2: score_factual += 2
    if len(found_terms) >= 4: score_factual += 2
    if any(char.isdigit() for char in cleaned_answer): score_factual += 1 # cited data or numbers
    if word_count >= 150: score_factual += 1
    score_factual = min(10, max(2, score_factual))
    
    if score_factual >= 8:
        factual_fb = f"Strong factual foundation citing domain concepts ({', '.join(found_terms[:3])}) and contextual mechanisms."
    elif score_factual >= 5:
        factual_fb = f"Moderate factual grounding ({', '.join(found_terms[:2]) if found_terms else 'general concepts'}). Incorporating specific statutory provisions or empirical data will heighten authority."
    else:
        factual_fb = "Relies largely on generalized assertions without citing concrete policies, legal frameworks, or empirical evidence."

    # 2. Relevance (0 - 10)
    score_relevance = 3
    if overlap >= 2: score_relevance += 2
    if overlap >= 4: score_relevance += 2
    if overlap >= 6: score_relevance += 2
    if word_count >= 120: score_relevance += 1
    score_relevance = min(10, max(2, score_relevance))
    
    if score_relevance >= 8:
        relevance_fb = f"Directly answers the prompt with high fidelity ({overlap} core keyword linkages). Maintained strong thematic focus."
    elif score_relevance >= 5:
        relevance_fb = f"Partially addresses the question with {overlap} thematic touchpoints, but exhibits secondary wandering into tangential areas."
    else:
        relevance_fb = "Weak topic adherence: Struggles to directly tackle the central dilemmas posed by the question."

    # 3. Structure & Clarity (0 - 10)
    intro_cues = ['introduction', 'firstly', 'to begin with', 'in context of', 'primarily', 'initially', 'fundamentally']
    transition_cues = ['furthermore', 'moreover', 'however', 'on the other hand', 'in contrast', 'additionally', 'consequently', 'secondly']
    conclusion_cues = ['in conclusion', 'to conclude', 'way forward', 'ultimately', 'in summary', 'overall', 'thus', 'recommendation']
    
    has_intro = any(c in text_lower for c in intro_cues)
    has_trans = any(c in text_lower for c in transition_cues)
    has_concl = any(c in text_lower for c in conclusion_cues)
    has_paras = '\n' in cleaned_answer
    
    score_structure = 3
    if has_intro: score_structure += 2
    if has_trans or has_paras: score_structure += 2
    if has_concl: score_structure += 2
    if word_count >= 150: score_structure += 1
    score_structure = min(10, max(2, score_structure))
    
    if score_structure >= 8:
        structure_fb = "Exemplary structural discipline: Clear introduction, transition signposting, and a decisive conclusion."
    elif score_structure >= 5:
        structure_fb = "Acceptable progression, but transitions between arguments felt abrupt. Use explicit rhetorical bridges ('Furthermore', 'On the counter-side')."
    else:
        structure_fb = "Run-on exposition: Lacks a clearly defined introduction or structured concluding summary."

    # 4. Depth of Analysis (0 - 10)
    analytical_dims = ['social', 'economic', 'political', 'ethical', 'technological', 'legal', 'global', 'security', 'governance', 'institutional', 'challenges', 'implications']
    matched_dims = [dim for dim in analytical_dims if dim in text_lower]
    
    score_depth = 3
    if len(matched_dims) >= 2: score_depth += 2
    if len(matched_dims) >= 4: score_depth += 3
    if any(k in text_lower for k in ['however', 'although', 'counter', 'risk', 'trade-off', 'challenge']): score_depth += 2 # balanced counter-perspective
    score_depth = min(10, max(2, score_depth))
    
    if score_depth >= 8:
        depth_fb = f"High analytical maturity: Multi-stakeholder analysis spanning {len(matched_dims)} dimensions with counter-balanced perspectives."
    elif score_depth >= 5:
        depth_fb = f"Covers primary dimensions ({', '.join(matched_dims[:2]) if matched_dims else 'surface policy'}), but could explore counter-arguments or unintended consequences more deeply."
    else:
        depth_fb = "Surface-level observations: Lacks multi-dimensional scrutiny (economic, legal, social trade-offs)."

    # 5. Time & Word Discipline (0 - 10)
    score_time = 4
    if 250 <= word_count <= 550:
        score_time = 9
    elif 180 <= word_count < 250:
        score_time = 7
    elif 100 <= word_count < 180:
        score_time = 5
    elif 50 <= word_count < 100:
        score_time = 3
    elif word_count > 700:
        score_time = 6 # too fast / word salad
    
    if time_taken_seconds >= 120 and score_time >= 7:
        score_time = min(10, score_time + 1)
        
    time_fb = f"Articulated {word_count} words across {time_taken_seconds}s. {'Optimal pacing for a 5-minute extempore.' if score_time >= 8 else 'Pacing needs adjustment for the 5-minute target duration.'}"

    total_score = score_factual + score_relevance + score_structure + score_depth + score_time
    
    if total_score >= 40:
        overall_fb = f"Distinguished performance scoring {total_score}/50! Your response exhibited high analytical clarity, domain relevance, and disciplined rhetorical flow. Polishing the conclusion with a sharp 3-point policy roadmap will position you in the top 1%."
    elif total_score >= 30:
        overall_fb = f"Solid, commendable delivery scoring {total_score}/50. Good grasp of the core dilemma. To climb into the superior band, strengthen the body with empirical references and explicitly signpost your transitions."
    elif total_score >= 20:
        overall_fb = f"Developing effort scoring {total_score}/50. The core idea is present, but the delivery lacks depth, structure, and verbal density for a 5-minute extempore. Practice brainstorming 3 distinct angles during the 60s prep phase."
    else:
        overall_fb = f"Needs substantial refinement ({total_score}/50). The response was brief, underdeveloped, or diverged from the prompt. Focus on structuring: 1 min Context ➔ 2.5 min Analysis ➔ 1.5 min Way Forward."

    model_answer_structure = (
        "1. Opening Hook & Context (1 Min): Define the core issue, cite the live headline, and clearly declare your thesis.\n"
        "2. Multi-Stakeholder Analysis (2.5 Mins): Examine institutional, socio-economic, and constitutional dimensions with a balanced counter-perspective.\n"
        "3. Pragmatic Way Forward (1.5 Mins): Propose actionable recommendations balancing regulatory oversight with practical execution."
    )

    return {
        'score_factual': score_factual,
        'factual_feedback': factual_fb,
        'score_relevance': score_relevance,
        'relevance_feedback': relevance_fb,
        'score_structure': score_structure,
        'structure_feedback': structure_fb,
        'score_depth': score_depth,
        'depth_feedback': depth_fb,
        'score_time': score_time,
        'time_feedback': time_fb,
        'total_score': total_score,
        'overall_feedback': overall_fb,
        'model_answer_structure': model_answer_structure,
        'ai_evaluator_type': 'Strict Rubric Examiner (UPSC Standard)'
    }
