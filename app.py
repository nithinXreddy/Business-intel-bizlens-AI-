import streamlit as st
import plotly.graph_objects as go
from scraper import fetch_reviews
from analyzer import run_full_analysis, generate_improvement_plan, chat_about_business

st.set_page_config(page_title="BizLens AI", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0a0a0f; color: #e8e8f0; }
.stApp { background: #0a0a0f; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1300px; margin: 0 auto; }
.hero-title { font-family: 'Syne', sans-serif; font-size: 3.2rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #60a5fa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; line-height: 1.1; }
.hero-sub { font-size: 1.05rem; color: #6b7280; margin-top: 0.5rem; }
.card { background: #13131a; border: 1px solid #1f1f2e; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
.card-accent { background: linear-gradient(135deg, #13131a 0%, #1a1225 100%); border: 1px solid #2d1f5e; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
.section-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #a78bfa; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 1rem; }
.pill-positive { display: inline-block; background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; margin: 3px; }
.pill-negative { display: inline-block; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: #f87171; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; margin: 3px; }
.pill-mixed { display: inline-block; background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.3); color: #fbbf24; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 500; margin: 3px; }
.rec-card { background: #0f0f18; border-left: 3px solid #a78bfa; border-radius: 0 12px 12px 0; padding: 1rem 1.2rem; margin-bottom: 0.8rem; }
.rec-high { border-left-color: #f87171; }
.rec-medium { border-left-color: #fbbf24; }
.rec-low { border-left-color: #4ade80; }
.rec-issue { font-weight: 600; font-size: 0.95rem; color: #e8e8f0; margin-bottom: 0.3rem; }
.rec-fix { font-size: 0.88rem; color: #9ca3af; line-height: 1.5; }
.rec-meta { font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem; }
.rec-quote { font-size: 0.8rem; color: #6366f1; font-style: italic; margin-top: 0.4rem; }
.plan-box { background: #0f0f18; border: 1px solid #1f1f2e; border-radius: 12px; padding: 1.2rem; white-space: pre-wrap; font-size: 0.9rem; line-height: 1.7; color: #d1d5db; }
.chat-user { background: #1e1b4b; border-radius: 12px 12px 4px 12px; padding: 0.8rem 1rem; margin: 0.5rem 0 0.5rem auto; font-size: 0.9rem; max-width: 80%; color: #e0e7ff; }
.chat-ai { background: #13131a; border: 1px solid #1f1f2e; border-radius: 12px 12px 12px 4px; padding: 0.8rem 1rem; margin: 0.5rem 0; font-size: 0.9rem; max-width: 85%; color: #d1d5db; line-height: 1.6; }
.biz-bar { background: linear-gradient(90deg, #13131a, #1a1225); border: 1px solid #2d1f5e; border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1.5rem; }
.biz-name { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700; color: #fff; }
.biz-meta { font-size: 0.85rem; color: #6b7280; margin-top: 0.3rem; }
.divider { border: none; border-top: 1px solid #1f1f2e; margin: 1.5rem 0; }
.metric-box { background: #13131a; border: 1px solid #1f1f2e; border-radius: 12px; padding: 1rem; text-align: center; }
.metric-val { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
.metric-lbl { font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.2rem; }
.vibe-box { background: linear-gradient(135deg, rgba(34,197,94,0.05), rgba(16,185,129,0.05)); border: 1px solid rgba(34,197,94,0.2); border-radius: 12px; padding: 1.2rem 1.5rem; margin-top: 1rem; }
.vibe-text { font-size: 0.95rem; color: #86efac; line-height: 1.6; font-style: italic; }
.quick-win { display: inline-block; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); color: #818cf8; padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; margin: 4px; font-weight: 500; }
.note-box { background: rgba(167,139,250,0.05); border: 1px solid rgba(167,139,250,0.2); border-radius: 10px; padding: 0.8rem 1rem; font-size: 0.82rem; color: #a78bfa; margin-bottom: 1rem; }
.stTextInput > div > div > input { background: #13131a !important; border: 1px solid #2d2d40 !important; border-radius: 12px !important; color: #e8e8f0 !important; font-family: 'Inter', sans-serif !important; padding: 0.8rem 1rem !important; }
.stTextInput > div > div > input:focus { border-color: #a78bfa !important; box-shadow: 0 0 0 2px rgba(167,139,250,0.15) !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; border: none !important; border-radius: 10px !important; font-family: 'Inter', sans-serif !important; font-weight: 600 !important; padding: 0.6rem 1.5rem !important; }
.stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "done": False, "reviews": None, "analysis": None,
    "info": None, "plan": None, "plan_done": False, "chat": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def score_color(s):
    return "#4ade80" if s >= 80 else "#fbbf24" if s >= 60 else "#f97316" if s >= 40 else "#f87171"

def render_stars(r):
    r = float(r or 0)
    return "★" * int(r) + "☆" * (5 - int(r))

def gauge(score):
    c = score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font": {"size": 48, "color": c, "family": "Syne"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#4b5563", "size": 10}, "tickcolor": "#1f1f2e"},
            "bar": {"color": c, "thickness": 0.25},
            "bgcolor": "#13131a", "bordercolor": "#1f1f2e", "borderwidth": 1,
            "steps": [
                {"range": [0, 40], "color": "rgba(248,113,113,0.08)"},
                {"range": [40, 70], "color": "rgba(251,191,36,0.08)"},
                {"range": [70, 100], "color": "rgba(74,222,128,0.08)"},
            ],
            "threshold": {"line": {"color": c, "width": 3}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(t=20, b=10, l=20, r=20), height=200)
    return fig

def radar(cats):
    if not cats: return None
    names = [c["name"] for c in cats]
    scores = [c.get("score", 5) for c in cats]
    fig = go.Figure(go.Scatterpolar(
        r=scores + [scores[0]], theta=names + [names[0]],
        fill="toself", fillcolor="rgba(167,139,250,0.12)",
        line=dict(color="#a78bfa", width=2), marker=dict(color="#a78bfa", size=6),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color="#4b5563", size=9), gridcolor="#1f1f2e", linecolor="#1f1f2e"),
            angularaxis=dict(tickfont=dict(color="#9ca3af", size=11), gridcolor="#1f1f2e", linecolor="#1f1f2e"),
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=30, r=30), height=300, showlegend=False,
    )
    return fig

def rating_bar(reviews):
    counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        k = int(r.get("rating", 0))
        if k in counts: counts[k] += 1
    fig = go.Figure(go.Bar(
        x=list(counts.values()), y=[f"{'★'*k}" for k in counts],
        orientation="h",
        marker=dict(color=["#4ade80","#86efac","#fbbf24","#f97316","#f87171"], line=dict(width=0)),
        text=list(counts.values()), textposition="outside",
        textfont=dict(color="#6b7280", size=11),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=5, b=5, l=5, r=40), height=160,
        xaxis=dict(visible=False),
        yaxis=dict(tickfont=dict(color="#fbbf24", size=13), gridcolor="#1f1f2e"),
        bargap=0.3,
    )
    return fig

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">BizLens AI</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Paste a Google Maps link → deep AI analysis of any business in seconds</p>', unsafe_allow_html=True)
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── URL Input ──────────────────────────────────────────────────────────────────
c1, c2 = st.columns([5, 1])
with c1:
    url = st.text_input("", placeholder="🔗  Paste Google Maps business URL here...", label_visibility="collapsed", key="url_input")
with c2:
    go_btn = st.button("Analyze →", use_container_width=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Trigger ────────────────────────────────────────────────────────────────────
if go_btn and url:
    for k in ["done", "reviews", "analysis", "info", "plan", "plan_done", "chat"]:
        st.session_state[k] = False if k == "done" or k == "plan_done" else ([] if k == "chat" else None)

    with st.spinner("🔍 Fetching business data from Google..."):
        result = fetch_reviews(url)

    if "error" in result:
        st.error(f"❌ {result['error']}")
        st.stop()

    if not result.get("reviews"):
        st.warning("⚠️ Business found but no written reviews available on Google Places.")
        st.stop()

    st.session_state.reviews = result["reviews"]
    st.session_state.info = result["business_info"]

    with st.spinner("🧠 Running AI analysis — takes about 15 seconds..."):
        st.session_state.analysis = run_full_analysis(
            result["business_info"]["name"],
            result["reviews"],
            result["business_info"],
        )
        st.session_state.done = True

    st.rerun()

# ── Dashboard ──────────────────────────────────────────────────────────────────
if st.session_state.done and st.session_state.analysis:
    info = st.session_state.info
    reviews = st.session_state.reviews
    an = st.session_state.analysis
    sent = an["sentiment"]
    health = an["health_score"]
    recs = an["recommendations"]

    # Note about review sample
    st.markdown(f"""
    <div class="note-box">
      ℹ️ Analysis based on <b>{len(reviews)} written reviews</b> sampled by Google Places API 
      + overall rating of <b>{info.get('rating')}★ from {info.get('total_reviews', 0):,} total reviews</b>.
      The AI uses both data sources for accurate insights.
    </div>
    """, unsafe_allow_html=True)

    # Business bar
    rating_str = f"{info.get('rating')} {render_stars(info.get('rating', 0))}" if info.get('rating') else ""
    st.markdown(f"""
    <div class="biz-bar">
      <div class="biz-name">📍 {info.get('name', '')}</div>
      <div class="biz-meta">
        {info.get('address', '')}
        {'&nbsp;·&nbsp;' + info.get('category','') if info.get('category') else ''}
        {'&nbsp;·&nbsp;' + info.get('price_level','') if info.get('price_level') else ''}
        {'&nbsp;·&nbsp;<span style="color:#fbbf24">' + rating_str + '</span>&nbsp;(' + str(info.get('total_reviews',0)) + ' reviews on Google)' if rating_str else ''}
      </div>
      {'<div class="biz-meta" style="margin-top:4px;font-style:italic;color:#4b5563">' + info.get("summary","") + '</div>' if info.get("summary") else ''}
    </div>
    """, unsafe_allow_html=True)

    # Row 1: score + ratings + stats
    col1, col2, col3 = st.columns([1.2, 1.2, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Business Health Score</p>', unsafe_allow_html=True)
        st.plotly_chart(gauge(health["score"]), use_container_width=True, config={"displayModeBar": False})
        gc = score_color(health["score"])
        st.markdown(f"""
        <div style="text-align:center;margin-top:-10px;">
          <span style="font-family:Syne;font-size:1.3rem;font-weight:700;color:{gc};">
            Grade: {health.get('grade','?')} — {health.get('score_label','')}
          </span><br>
          <span style="font-size:0.82rem;color:#6b7280;display:block;margin-top:4px;">
            {health.get('one_line_verdict','')}
          </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Rating Breakdown (Sample)</p>', unsafe_allow_html=True)
        st.plotly_chart(rating_bar(reviews), use_container_width=True, config={"displayModeBar": False})
        bd = health.get("score_breakdown", {})
        st.markdown(f"""
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:0.5rem;">
          <div class="metric-box" style="flex:1;min-width:60px"><div class="metric-val">{bd.get('rating_score',0)}<span style="font-size:0.9rem;color:#4b5563">/35</span></div><div class="metric-lbl">Rating</div></div>
          <div class="metric-box" style="flex:1;min-width:60px"><div class="metric-val">{bd.get('sentiment_score',0)}<span style="font-size:0.9rem;color:#4b5563">/25</span></div><div class="metric-lbl">Sentiment</div></div>
          <div class="metric-box" style="flex:1;min-width:60px"><div class="metric-val">{bd.get('volume_score',0)}<span style="font-size:0.9rem;color:#4b5563">/20</span></div><div class="metric-lbl">Volume</div></div>
          <div class="metric-box" style="flex:1;min-width:60px"><div class="metric-val">{bd.get('complaint_severity_score',0)}<span style="font-size:0.9rem;color:#4b5563">/20</span></div><div class="metric-lbl">Severity</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Quick Stats</p>', unsafe_allow_html=True)
        total_s = len(reviews)
        pos = sum(1 for r in reviews if r.get("rating", 0) >= 4)
        neg = sum(1 for r in reviews if r.get("rating", 0) <= 2)
        avg = sum(r.get("rating", 0) for r in reviews) / total_s if total_s else 0
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:10px;">
          <div class="metric-box"><div class="metric-val">{info.get('total_reviews',0):,}</div><div class="metric-lbl">Total Google Reviews</div></div>
          <div class="metric-box"><div class="metric-val" style="color:#4ade80">{round(pos/total_s*100) if total_s else 0}%</div><div class="metric-lbl">Positive in Sample</div></div>
          <div class="metric-box"><div class="metric-val" style="color:#f87171">{round(neg/total_s*100) if total_s else 0}%</div><div class="metric-lbl">Negative in Sample</div></div>
          <div class="metric-box"><div class="metric-val">{info.get('rating','?')}★</div><div class="metric-lbl">Google Rating</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Row 2: Sentiment + Radar
    cl, cr = st.columns([1.4, 1])
    with cl:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Sentiment by Category</p>', unsafe_allow_html=True)
        for cat in sent.get("categories", []):
            s = cat.get("sentiment", "mixed")
            sc = cat.get("score", 5)
            st.markdown(f"""
            <div style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #1f1f2e;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                <span style="font-weight:600;font-size:0.95rem;color:#e8e8f0">{cat.get('name','')}</span>
                <span class="pill-{s}">{s.upper()} · {sc}/10</span>
              </div>
              <div>{''.join(f'<span style="font-size:0.8rem;color:#4ade80;margin-right:8px">✓ {p}</span>' for p in cat.get('positives',[]))}</div>
              <div>{''.join(f'<span style="font-size:0.8rem;color:#f87171;margin-right:8px">✗ {n}</span>' for n in cat.get('negatives',[]))}</div>
              <div style="font-size:0.75rem;color:#4b5563;margin-top:0.3rem">Mentioned in ~{cat.get('review_count',0)} reviews</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Category Radar</p>', unsafe_allow_html=True)
        r_fig = radar(sent.get("categories", []))
        if r_fig:
            st.plotly_chart(r_fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        vibe = sent.get("overall_vibe", "")
        if vibe:
            st.markdown(f"""
            <div class="vibe-box">
              <div style="font-size:0.75rem;font-weight:600;color:#4ade80;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem">✦ What's working</div>
              <div class="vibe-text">"{vibe}"</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Row 3: Recommendations
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Actionable Recommendations</p>', unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    for i, rec in enumerate(recs.get("recommendations", [])):
        impact = rec.get("impact", "medium")
        with (rc1 if i % 2 == 0 else rc2):
            quote = f'<div class="rec-quote">"{rec.get("example_review_quote","")}"</div>' if rec.get("example_review_quote") else ""
            st.markdown(f"""
            <div class="rec-card rec-{impact}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.3rem">
                <div class="rec-issue">#{rec.get('priority',i+1)} {rec.get('issue','')}</div>
                <span class="pill-{'negative' if impact=='high' else 'mixed' if impact=='medium' else 'positive'}">{impact.upper()}</span>
              </div>
              <div class="rec-fix">→ {rec.get('fix','')}</div>
              {quote}
              <div class="rec-meta">⏱ {rec.get('timeline','')} &nbsp;·&nbsp; Effort: {rec.get('effort','').title()}</div>
            </div>
            """, unsafe_allow_html=True)

    qw = recs.get("quick_wins", [])
    if qw:
        st.markdown("<div style='margin-top:1rem'><span style='font-size:0.85rem;color:#6b7280;font-weight:500'>⚡ Quick wins you can do today:</span><br>", unsafe_allow_html=True)
        st.markdown("".join(f'<span class="quick-win">✓ {w}</span>' for w in qw), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 30-day plan
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    p1, p2 = st.columns([2, 1])
    with p1:
        st.markdown("""
        <div style="margin-bottom:0.8rem">
          <span style="font-family:Syne;font-size:1.2rem;font-weight:700;color:#e8e8f0">🚀 Auto Business Consultant Mode</span><br>
          <span style="font-size:0.85rem;color:#6b7280">Get a personalised week-by-week improvement plan</span>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        plan_btn = st.button("✨ Improve My Business →", use_container_width=True)

    if plan_btn and not st.session_state.plan_done:
        with st.spinner("🗓 Generating your 30-day plan..."):
            st.session_state.plan = generate_improvement_plan(
                info.get("name", "Your Business"), sent, recs
            )
            st.session_state.plan_done = True
        st.rerun()

    if st.session_state.plan_done and st.session_state.plan:
        st.markdown('<div class="card-accent">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">📅 Your 30-Day Improvement Plan</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="plan-box">{st.session_state.plan}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:1rem">
      <span style="font-family:Syne;font-size:1.2rem;font-weight:700;color:#e8e8f0">💬 Ask Anything About This Business</span><br>
      <span style="font-size:0.85rem;color:#6b7280">Chat with an AI consultant who knows all the data</span>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat:
        cls = "chat-user" if msg["role"] == "user" else "chat-ai"
        prefix = "" if msg["role"] == "user" else "🤖 "
        st.markdown(f'<div class="{cls}">{prefix}{msg["content"]}</div>', unsafe_allow_html=True)

    ch1, ch2 = st.columns([5, 1])
    with ch1:
        question = st.text_input("", placeholder="e.g. How do I fix the wait time issue? What should I prioritise?", label_visibility="collapsed", key="chat_input")
    with ch2:
        send = st.button("Send →", use_container_width=True)

    if send and question:
        st.session_state.chat.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            reply = chat_about_business(question, info.get("name", ""), an, st.session_state.chat[:-1])
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#374151">
      <div style="font-size:3rem;margin-bottom:1rem">🔍</div>
      <div style="font-family:Syne;font-size:1.1rem;font-weight:600;color:#4b5563;margin-bottom:0.5rem">
        Paste any Google Maps business link above to get started
      </div>
      <div style="font-size:0.85rem;color:#374151;line-height:1.7">
        Business Health Score &nbsp;·&nbsp; Sentiment by Category &nbsp;·&nbsp;
        Actionable Recommendations &nbsp;·&nbsp; 30-Day Plan &nbsp;·&nbsp; AI Chat
      </div>
    </div>
    """, unsafe_allow_html=True)