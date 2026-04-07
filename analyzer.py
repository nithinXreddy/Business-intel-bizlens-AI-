import json
from groq import Groq

# ── PASTE YOUR KEY HERE ───────────────────────────────────────────────────────
GROQ_API_KEY = "Api_key"
# ─────────────────────────────────────────────────────────────────────────────

client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"


def _llm(prompt: str, max_tokens: int = 2000) -> str:
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return r.choices[0].message.content


def _llm_json(prompt: str) -> dict:
    text = _llm(prompt).strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        text = "\n".join(lines).strip()
    return json.loads(text)


def _format_reviews(reviews: list) -> str:
    if not reviews:
        return "No written reviews available."
    out = []
    for i, r in enumerate(reviews, 1):
        stars = "★" * int(r.get("rating", 0)) + "☆" * (5 - int(r.get("rating", 0)))
        out.append(f"[{i}] {stars} {r.get('rating')}/5 — {r.get('text', '').strip()}")
    return "\n\n".join(out)


def analyze_sentiment(reviews: list, info: dict) -> dict:
    prompt = f"""You are an expert business analyst. Analyze this business.

BUSINESS: {info.get('name')}
TYPE: {info.get('category', 'Business')}
GOOGLE RATING: {info.get('rating')}/5 stars from {info.get('total_reviews', 0)} total reviews
PRICE LEVEL: {info.get('price_level', 'Unknown')}

WRITTEN REVIEWS ({len(reviews)} samples):
{_format_reviews(reviews)}

NOTE: Use BOTH the written reviews AND the overall {info.get('rating')}/5 rating from {info.get('total_reviews', 0)} customers 
to give a complete picture. The overall rating is statistically very meaningful.

Return ONLY raw JSON, no markdown, no backticks:
{{
  "categories": [
    {{
      "name": "Category Name",
      "sentiment": "positive",
      "score": 8,
      "positives": ["specific point 1"],
      "negatives": ["specific point 1"],
      "review_count": 2
    }}
  ],
  "top_praise": "One sentence about what customers love most.",
  "top_complaint": "One sentence about the biggest problem.",
  "overall_vibe": "Warm 1-2 sentences about genuine strengths, written encouragingly for the owner."
}}

Rules:
- 4-6 categories relevant to this business type
- sentiment must be exactly: positive, negative, or mixed
- score is 1-10
- Be specific with real details from reviews
- Return ONLY the JSON object"""

    return _llm_json(prompt)


def calculate_health_score(reviews: list, info: dict, sentiment: dict) -> dict:
    sample_ratings = [r.get("rating", 0) for r in reviews if r.get("rating")]
    five_star = sum(1 for r in sample_ratings if r == 5)
    one_star = sum(1 for r in sample_ratings if r == 1)

    prompt = f"""Calculate a business health score for "{info.get('name')}".

KEY DATA:
- Overall Google rating: {info.get('rating')}/5 from {info.get('total_reviews', 0)} total reviews
- Sample reviews analyzed: {len(reviews)}
- 5-star in sample: {five_star}, 1-star in sample: {one_star}

SENTIMENT:
{json.dumps(sentiment.get('categories', []), indent=2)}

Top praise: {sentiment.get('top_praise', '')}
Top complaint: {sentiment.get('top_complaint', '')}

Score 0-100 with these weights:
- Google overall rating (35pts): {info.get('rating')}/5 → max 35pts
- Sentiment quality (25pts): based on category scores
- Review volume/social proof (20pts): {info.get('total_reviews', 0)} reviews
- Complaint severity (20pts): how bad are the problems

Return ONLY raw JSON:
{{
  "score": 74,
  "grade": "B",
  "score_breakdown": {{
    "rating_score": 26,
    "sentiment_score": 20,
    "volume_score": 16,
    "complaint_severity_score": 12
  }},
  "score_label": "Good",
  "one_line_verdict": "Honest one sentence for the owner about where they stand."
}}

Grade scale: A=90+, B=75-89, C=55-74, D=40-54, F=below 40
Label: Excellent=85+, Good=70-84, Needs Attention=50-69, Critical=below 50
Return ONLY the JSON."""

    return _llm_json(prompt)


def generate_recommendations(reviews: list, info: dict, sentiment: dict) -> dict:
    problem_cats = [c["name"] for c in sentiment.get("categories", []) if c.get("sentiment") in ["negative", "mixed"]]

    prompt = f"""You are a top business consultant for "{info.get('name')}".

OVERALL RATING: {info.get('rating')}/5 from {info.get('total_reviews', 0)} Google reviews
TOP COMPLAINT: {sentiment.get('top_complaint', '')}
PROBLEM AREAS: {', '.join(problem_cats) if problem_cats else 'None identified'}

REVIEWS:
{_format_reviews(reviews)}

Give 5 specific actionable recommendations ranked by urgency.
Return ONLY raw JSON:
{{
  "recommendations": [
    {{
      "priority": 1,
      "issue": "Specific problem",
      "fix": "Concrete specific action — no generic advice",
      "impact": "high",
      "effort": "easy",
      "timeline": "This week",
      "example_review_quote": "Short paraphrase under 10 words"
    }}
  ],
  "quick_wins": [
    "Specific action owner can do TODAY",
    "Another quick win this week",
    "A third quick action"
  ]
}}

impact: high/medium/low | effort: easy/medium/hard | timeline: This week/This month/Next quarter
Return ONLY the JSON."""

    return _llm_json(prompt)


def generate_improvement_plan(business_name: str, sentiment: dict, recommendations: dict) -> str:
    issues = [r["issue"] for r in recommendations.get("recommendations", [])[:3]]
    wins = recommendations.get("quick_wins", [])

    prompt = f"""Write a 30-day improvement plan for "{business_name}".

TOP ISSUES:
{chr(10).join(f'- {i}' for i in issues)}

QUICK WINS:
{chr(10).join(f'- {w}' for w in wins)}

Format exactly like this:

WEEK 1 — [Theme Title]
- Action 1
- Action 2  
- Action 3
Expected outcome: [result]

WEEK 2 — [Theme Title]
- Action 1
- Action 2
- Action 3
Expected outcome: [result]

WEEK 3 — [Theme Title]
- Action 1
- Action 2
- Action 3
Expected outcome: [result]

WEEK 4 — [Theme Title]
- Action 1
- Action 2
- Action 3
Expected outcome: [result]

Write directly to the owner as "you". Be specific and realistic. 350-400 words total."""

    return _llm(prompt, max_tokens=1000)


def chat_about_business(user_message: str, business_name: str, context: dict, history: list) -> str:
    h = context.get("health_score", {})
    s = context.get("sentiment", {})
    r = context.get("recommendations", {})

    ctx = f"""BUSINESS: {business_name}
HEALTH SCORE: {h.get('score')}/100 — {h.get('score_label')}
VERDICT: {h.get('one_line_verdict')}
TOP PRAISE: {s.get('top_praise')}
TOP COMPLAINT: {s.get('top_complaint')}
VIBE: {s.get('overall_vibe')}
CATEGORIES: {json.dumps(s.get('categories', []))}
TOP RECOMMENDATIONS: {json.dumps(r.get('recommendations', [])[:3])}"""

    conv = ""
    for msg in history[-6:]:
        conv += f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}\n\n"

    prompt = f"""You are an expert business analyst for {business_name}.

{ctx}

CONVERSATION:
{conv}User: {user_message}

Answer specifically using the data above. 2-3 paragraphs max. Speak as a trusted consultant."""

    return _llm(prompt, max_tokens=800)


def run_full_analysis(business_name: str, reviews: list, business_info: dict = None) -> dict:
    if not business_info:
        business_info = {"name": business_name}
    sentiment = analyze_sentiment(reviews, business_info)
    health = calculate_health_score(reviews, business_info, sentiment)
    recommendations = generate_recommendations(reviews, business_info, sentiment)
    return {"sentiment": sentiment, "health_score": health, "recommendations": recommendations}