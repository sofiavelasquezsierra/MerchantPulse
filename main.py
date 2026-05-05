import streamlit as st
import anthropic
import json
import csv
import io
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MerchantPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* ── Hero banner ── */
  .hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    border-radius: 16px;
    padding: 2.2rem 2.5rem 1.8rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
  }
  .hero::after {
    content: "";
    position: absolute;
    bottom: -40px; left: 30%;
    width: 140px; height: 140px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
  }
  .hero-title {
    font-size: 2.6rem;
    font-weight: 900;
    color: #fff;
    line-height: 1.1;
    margin: 0 0 0.5rem;
    letter-spacing: -0.02em;
  }
  .hero-sub {
    font-size: 1.05rem;
    color: rgba(255,255,255,0.82);
    margin: 0;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.2rem 0.7rem;
    border-radius: 99px;
    margin-bottom: 0.7rem;
    border: 1px solid rgba(255,255,255,0.25);
  }

  /* ── Stat cards ── */
  .stat-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.6rem;
  }
  .stat-card {
    flex: 1;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }
  .stat-card-purple { background: linear-gradient(135deg,#ede9fe,#ddd6fe); border: 1px solid #c4b5fd; }
  .stat-card-green  { background: linear-gradient(135deg,#dcfce7,#bbf7d0); border: 1px solid #86efac; }
  .stat-card-red    { background: linear-gradient(135deg,#fee2e2,#fecaca); border: 1px solid #fca5a5; }
  .stat-card-amber  { background: linear-gradient(135deg,#fef9c3,#fef08a); border: 1px solid #fde047; }
  .stat-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; color: #64748b; }
  .stat-value { font-size: 1.75rem; font-weight: 900; color: #1e1b4b; line-height: 1; }
  .stat-sub   { font-size: 0.78rem; color: #64748b; margin-top: 0.1rem; }

  /* ── Sentiment bar ── */
  .sent-wrap { margin: 0.6rem 0 1.4rem; }
  .sent-bar {
    display: flex;
    border-radius: 10px;
    overflow: hidden;
    height: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 0.55rem;
  }
  .sent-pos {
    background: linear-gradient(90deg,#16a34a,#22c55e);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 800; font-size: 0.82rem;
    transition: width 0.8s ease;
  }
  .sent-neu {
    background: linear-gradient(90deg,#64748b,#94a3b8);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 800; font-size: 0.82rem;
  }
  .sent-neg {
    background: linear-gradient(90deg,#dc2626,#ef4444);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 800; font-size: 0.82rem;
  }
  .sent-legend {
    display: flex; gap: 1.4rem; flex-wrap: wrap;
  }
  .sent-legend-item {
    display: flex; align-items: center; gap: 0.35rem;
    font-size: 0.82rem; color: #374151;
  }
  .sent-dot {
    width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
  }

  /* ── Section headers ── */
  .sec-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.6rem 0 0.8rem;
  }
  .sec-icon {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
  }
  .sec-icon-red    { background: linear-gradient(135deg,#fee2e2,#fca5a5); }
  .sec-icon-amber  { background: linear-gradient(135deg,#fef9c3,#fde047); }
  .sec-icon-purple { background: linear-gradient(135deg,#ede9fe,#c4b5fd); }
  .sec-icon-green  { background: linear-gradient(135deg,#dcfce7,#86efac); }
  .sec-icon-blue   { background: linear-gradient(135deg,#dbeafe,#93c5fd); }
  .sec-title { font-size: 1rem; font-weight: 700; color: #1e1b4b; }

  /* ── Pain point cards ── */
  .pain-card {
    background: #fff;
    border: 1px solid #fee2e2;
    border-left: 4px solid #ef4444;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.55rem;
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    box-shadow: 0 1px 4px rgba(239,68,68,0.07);
    transition: box-shadow 0.2s;
  }
  .pain-card:hover { box-shadow: 0 4px 12px rgba(239,68,68,0.13); }
  .pain-num {
    background: linear-gradient(135deg,#ef4444,#dc2626);
    color: #fff; font-weight: 800; font-size: 0.72rem;
    width: 22px; height: 22px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
  }
  .pain-text { font-size: 0.91rem; color: #374151; line-height: 1.5; }

  /* ── Feature chips ── */
  .feature-card {
    background: #fff;
    border: 1px solid #e0e7ff;
    border-left: 4px solid #6366f1;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.55rem;
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    box-shadow: 0 1px 4px rgba(99,102,241,0.07);
    transition: box-shadow 0.2s;
  }
  .feature-card:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.13); }
  .feat-num {
    background: linear-gradient(135deg,#6366f1,#4f46e5);
    color: #fff; font-weight: 800; font-size: 0.72rem;
    width: 22px; height: 22px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
  }
  .feat-text { font-size: 0.91rem; color: #374151; line-height: 1.5; }

  /* ── Action cards ── */
  .action-card-1 {
    background: linear-gradient(135deg,#faf5ff,#ede9fe);
    border: 1px solid #c4b5fd;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    display: flex; gap: 1rem; align-items: flex-start;
    box-shadow: 0 2px 8px rgba(124,58,237,0.1);
  }
  .action-card-2 {
    background: linear-gradient(135deg,#f0fdf4,#dcfce7);
    border: 1px solid #86efac;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    display: flex; gap: 1rem; align-items: flex-start;
  }
  .action-card-3 {
    background: linear-gradient(135deg,#fefce8,#fef9c3);
    border: 1px solid #fde047;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    display: flex; gap: 1rem; align-items: flex-start;
  }
  .action-circle {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 900; font-size: 1rem; flex-shrink: 0; color: #fff;
  }
  .ac1 { background: linear-gradient(135deg,#7c3aed,#4f46e5); }
  .ac2 { background: linear-gradient(135deg,#16a34a,#059669); }
  .ac3 { background: linear-gradient(135deg,#d97706,#b45309); }
  .action-body { flex: 1; }
  .action-title { font-size: 0.93rem; font-weight: 600; color: #1e1b4b; line-height: 1.5; }
  .high-badge {
    display: inline-block;
    background: linear-gradient(90deg,#7c3aed,#4f46e5);
    color: #fff; font-size: 0.62rem; font-weight: 800;
    padding: 0.18rem 0.6rem; border-radius: 99px;
    letter-spacing: 0.07em; text-transform: uppercase;
    margin-left: 0.5rem; vertical-align: middle;
  }

  /* ── Quote block ── */
  .quote-wrap {
    background: linear-gradient(135deg,#f0fdf4,#dcfce7);
    border: 1px solid #86efac;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative;
    margin: 0.5rem 0;
  }
  .quote-mark {
    font-size: 4rem; line-height: 1; color: #22c55e;
    opacity: 0.35; position: absolute;
    top: 0.3rem; left: 1rem;
    font-family: Georgia, serif;
  }
  .quote-text {
    font-style: italic; font-size: 1.05rem; color: #166534;
    line-height: 1.7; padding-left: 1.6rem; font-weight: 500;
  }

  /* ── Summary box ── */
  .summary-wrap {
    background: linear-gradient(135deg,#eff6ff,#dbeafe);
    border: 1px solid #93c5fd;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    color: #1e3a5f;
    font-size: 0.97rem;
    line-height: 1.75;
    margin: 0.5rem 0;
  }

  /* ── Sidebar ── */
  .sidebar-logo {
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #fff;
    margin-bottom: 1rem;
  }
  .sidebar-logo-title { font-size: 1.3rem; font-weight: 800; color: #fff; margin: 0; }
  .sidebar-logo-sub   { font-size: 0.78rem; color: rgba(255,255,255,0.75); margin: 0.2rem 0 0; }

  .sidebar-step {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 0.5rem 0.75rem;
    margin-bottom: 0.4rem; font-size: 0.85rem; color: #374151;
    display: flex; gap: 0.5rem; align-items: flex-start;
  }
  .step-num {
    background: linear-gradient(135deg,#6366f1,#4f46e5);
    color: #fff; font-weight: 700; font-size: 0.65rem;
    width: 18px; height: 18px; border-radius: 5px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 1px;
  }

  /* ── Input area polish ── */
  .input-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
  }

  /* ── Results divider ── */
  .results-header {
    background: linear-gradient(90deg,#4f46e5,#7c3aed,#a855f7);
    border-radius: 10px;
    padding: 0.7rem 1.2rem;
    color: #fff;
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    margin: 1.5rem 0 1rem;
  }

  /* ── Button overrides ── */
  div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 14px rgba(79,70,229,0.35) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
  }
  div[data-testid="stButton"] button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.45) !important;
  }
  div[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg,#059669,#047857) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(5,150,105,0.3) !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Sample reviews ─────────────────────────────────────────────────────────────
SAMPLE_REVIEWS = """Love this water bottle! Keeps my drinks cold for 24 hours easily. The lid is a bit tricky to open with one hand though.
The insulation is incredible — ice lasted 3 days in the summer heat. Would love a straw lid option.
Bought this for hiking. Great bottle but it's too wide to fit in my backpack's side pocket. Fix the diameter please!
Really disappointed. The paint chipped after just 2 weeks of normal use. Expected better quality for this price.
Perfect size for the gym. Wish it came in more color options — only basic colors available right now.
Leaks if you put it in a bag sideways. Otherwise the bottle itself is great. The lid seal needs work.
Amazing quality! Has held up to 8 months of daily use. The handle is super convenient. Only wish it had a loop for carabiners.
The bottle is beautiful but the mouth opening is too narrow for ice cubes. Have to chip ice to fit them in.
Keeps coffee hot for 6 hours — exactly as advertised. Cleaning is easy with the wide-mouth design. 10/10 recommend.
Great product overall. One issue: the bottom scratches easily and looks worn after just a month. Some kind of rubber base would help.
I bought 3 of these as gifts and everyone loves them. The only feedback I've gotten is that they want a smaller 12oz version.
The vacuum seal failed after 4 months — drinks are no longer staying cold. Reached out to support but got no response yet.
Absolutely love the design. Sleek, minimal, and fits perfectly in car cup holders. A built-in filter for fruit infusions would make it perfect.
Good bottle but the lid rattles a little when you shake it. Seems like a quality control issue on my unit.
Been using this daily for a year. Solid performer. My one ask: a carrying sleeve or pouch to go with it would complete the package."""

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <p class="sidebar-logo-title">📊 MerchantPulse</p>
      <p class="sidebar-logo-sub">AI-powered review analysis</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**What is this?**")
    st.markdown(
        "<span style='font-size:0.87rem;color:#555;'>MerchantPulse uses AI to turn your "
        "product reviews into a structured brief — surfacing pain points, feature requests, "
        "and prioritized recommendations in seconds.</span>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>**How to use**", unsafe_allow_html=True)
    for num, step in [
        ("1", "Paste reviews or upload a CSV with a `review` column"),
        ("2", "Add your product name for extra context (optional)"),
        ("3", "Click **Analyze Reviews**"),
        ("4", "Download the report when done"),
    ]:
        st.markdown(
            f'<div class="sidebar-step"><span class="step-num">{num}</span>{step}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "<span style='font-size:0.82rem;color:#555;'>Built with "
        "[Claude AI](https://anthropic.com) by **Sofia Velasquez Sierra**</span>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "[GitHub](https://github.com/sofiavelasquezsierra/merchantpulse) · "
        "[LinkedIn](https://linkedin.com/in/sofia-velasquez)"
    )

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">✦ Powered by Claude AI</div>
  <p class="hero-title">📊 MerchantPulse</p>
  <p class="hero-sub">Turn customer reviews into product decisions — in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
col_input, col_meta = st.columns([3, 1])

with col_meta:
    product_name = st.text_input(
        "Product name (optional)",
        placeholder="e.g. HydroMax Water Bottle",
        help="Give Claude context about which product these reviews are for.",
    )

with col_input:
    tab_paste, tab_upload = st.tabs(["📋 Paste Reviews", "📁 Upload CSV"])

    with tab_paste:
        if "review_text" not in st.session_state:
            st.session_state.review_text = ""

        review_text = st.text_area(
            "Paste reviews here (one per line or comma-separated)",
            value=st.session_state.review_text,
            height=180,
            placeholder="Paste your customer reviews here…",
            key="review_area",
        )
        if st.button("✨ Load sample reviews", type="secondary"):
            st.session_state.review_text = SAMPLE_REVIEWS
            st.rerun()

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload a CSV file with a `review` column",
            type=["csv"],
            help="CSV must contain a column named `review`.",
        )
        csv_reviews = ""
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode("utf-8")
                reader = csv.DictReader(io.StringIO(content))
                rows = list(reader)
                if "review" not in (reader.fieldnames or []):
                    st.error("CSV must have a column named `review`.")
                else:
                    csv_reviews = "\n".join(
                        r["review"] for r in rows if r.get("review", "").strip()
                    )
                    st.success(f"✅ Loaded {len(rows)} reviews from CSV.")
            except Exception as e:
                st.error(f"Could not read CSV: {e}")

# ── Collect final reviews ──────────────────────────────────────────────────────
active_reviews = csv_reviews if csv_reviews else st.session_state.get("review_text", review_text)

st.markdown("<br>", unsafe_allow_html=True)
analyze_clicked = st.button("🔍 Analyze Reviews", type="primary", use_container_width=True)

# ── Claude call ────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a product analyst helping a Shopify merchant understand what their customers want. Analyze the provided product reviews and return a JSON object with exactly these fields:
- top_pain_points: array of up to 5 strings, each a specific customer pain point with frequency estimate (e.g. 'Sizing runs small — mentioned in ~40% of reviews')
- feature_requests: array of up to 5 strings, each a specific feature or improvement customers want
- sentiment: object with keys 'positive' (%), 'neutral' (%), 'negative' (%) that sum to 100
- priority_actions: array of up to 3 strings, each a concrete recommendation for what the merchant should build, fix, or change — ordered by impact
- key_quote: one verbatim quote from the reviews that best summarizes the overall customer sentiment
- summary: 2-3 sentence plain English summary of what customers think

Return only valid JSON. No markdown, no explanation."""


def call_claude(reviews: str, product: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found. Add it to your .env file.")

    client = anthropic.Anthropic(api_key=api_key)
    context = f"Product: {product}\n\n" if product.strip() else ""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"{context}Reviews:\n{reviews}"}],
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if Claude wrapped the JSON
    cleaned = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return {"ok": True, "data": json.loads(cleaned), "raw": raw}
    except json.JSONDecodeError:
        return {"ok": False, "data": None, "raw": raw}


# ── Render helpers ─────────────────────────────────────────────────────────────
def render_stat_cards(data: dict, review_count: int):
    s = data.get("sentiment", {})
    pos = s.get("positive", 0)
    pain_count = len(data.get("top_pain_points", []))
    feat_count = len(data.get("feature_requests", []))
    dominant = "Positive" if pos >= 60 else ("Mixed" if pos >= 40 else "Negative")
    dominant_color = "#16a34a" if pos >= 60 else ("#d97706" if pos >= 40 else "#dc2626")

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card stat-card-purple">
        <span class="stat-label">Reviews analyzed</span>
        <span class="stat-value">{review_count}</span>
        <span class="stat-sub">total inputs</span>
      </div>
      <div class="stat-card stat-card-green">
        <span class="stat-label">Positive sentiment</span>
        <span class="stat-value">{pos}%</span>
        <span class="stat-sub" style="color:{dominant_color};font-weight:700;">{dominant}</span>
      </div>
      <div class="stat-card stat-card-red">
        <span class="stat-label">Pain points found</span>
        <span class="stat-value">{pain_count}</span>
        <span class="stat-sub">issues flagged</span>
      </div>
      <div class="stat-card stat-card-amber">
        <span class="stat-label">Feature requests</span>
        <span class="stat-value">{feat_count}</span>
        <span class="stat-sub">from customers</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_sentiment_bar(sentiment: dict):
    pos = sentiment.get("positive", 0)
    neu = sentiment.get("neutral", 0)
    neg = sentiment.get("negative", 0)
    st.markdown(f"""
    <div class="sent-wrap">
      <div class="sent-bar">
        <div class="sent-pos" style="width:{pos}%">{"▲ " + str(pos) + "%" if pos > 9 else ""}</div>
        <div class="sent-neu" style="width:{neu}%">{"● " + str(neu) + "%" if neu > 9 else ""}</div>
        <div class="sent-neg" style="width:{neg}%">{"▼ " + str(neg) + "%" if neg > 9 else ""}</div>
      </div>
      <div class="sent-legend">
        <div class="sent-legend-item"><div class="sent-dot" style="background:#22c55e;"></div>Positive — <b>{pos}%</b></div>
        <div class="sent-legend-item"><div class="sent-dot" style="background:#94a3b8;"></div>Neutral — <b>{neu}%</b></div>
        <div class="sent-legend-item"><div class="sent-dot" style="background:#ef4444;"></div>Negative — <b>{neg}%</b></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_results(data: dict, review_count: int):
    st.markdown('<div class="results-header">✦ Analysis Results</div>', unsafe_allow_html=True)

    render_stat_cards(data, review_count)

    # Sentiment
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon sec-icon-green">📊</div>
      <span class="sec-title">Sentiment Breakdown</span>
    </div>""", unsafe_allow_html=True)
    render_sentiment_bar(data.get("sentiment", {}))

    # Pain points + Feature requests
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
        <div class="sec-header">
          <div class="sec-icon sec-icon-red">🔴</div>
          <span class="sec-title">Top Pain Points</span>
        </div>""", unsafe_allow_html=True)
        for i, point in enumerate(data.get("top_pain_points", []), 1):
            st.markdown(
                f'<div class="pain-card"><div class="pain-num">{i}</div>'
                f'<div class="pain-text">{point}</div></div>',
                unsafe_allow_html=True,
            )

    with col_right:
        st.markdown("""
        <div class="sec-header">
          <div class="sec-icon sec-icon-amber">💡</div>
          <span class="sec-title">Feature Requests</span>
        </div>""", unsafe_allow_html=True)
        for i, feat in enumerate(data.get("feature_requests", []), 1):
            st.markdown(
                f'<div class="feature-card"><div class="feat-num">{i}</div>'
                f'<div class="feat-text">{feat}</div></div>',
                unsafe_allow_html=True,
            )

    # Priority actions
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon sec-icon-purple">🚀</div>
      <span class="sec-title">Priority Actions</span>
    </div>""", unsafe_allow_html=True)

    card_styles = ["action-card-1", "action-card-2", "action-card-3"]
    circle_styles = ["ac1", "ac2", "ac3"]
    for i, action in enumerate(data.get("priority_actions", []), 1):
        badge = '<span class="high-badge">⭐ High Impact</span>' if i == 1 else ""
        st.markdown(f"""
        <div class="{card_styles[i-1]}">
          <div class="action-circle {circle_styles[i-1]}">{i}</div>
          <div class="action-body">
            <div class="action-title">{action}{badge}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Key quote
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon sec-icon-green">💬</div>
      <span class="sec-title">Key Quote</span>
    </div>""", unsafe_allow_html=True)
    quote = data.get("key_quote", "")
    st.markdown(f"""
    <div class="quote-wrap">
      <div class="quote-mark">"</div>
      <div class="quote-text">{quote}</div>
    </div>""", unsafe_allow_html=True)

    # Summary
    st.markdown("""
    <div class="sec-header">
      <div class="sec-icon sec-icon-blue">📝</div>
      <span class="sec-title">Plain English Summary</span>
    </div>""", unsafe_allow_html=True)
    st.markdown(
        f'<div class="summary-wrap">{data.get("summary", "")}</div>',
        unsafe_allow_html=True,
    )


def build_markdown_report(data: dict, product: str) -> str:
    s = data.get("sentiment", {})
    lines = [
        f"# MerchantPulse Report{': ' + product if product else ''}",
        "",
        "## Sentiment Breakdown",
        f"- 🟢 Positive: {s.get('positive', 0)}%",
        f"- ⚪ Neutral:  {s.get('neutral', 0)}%",
        f"- 🔴 Negative: {s.get('negative', 0)}%",
        "",
        "## Top Pain Points",
    ]
    for i, p in enumerate(data.get("top_pain_points", []), 1):
        lines.append(f"{i}. 🔴 {p}")
    lines += ["", "## Feature Requests"]
    for i, f in enumerate(data.get("feature_requests", []), 1):
        lines.append(f"{i}. 💡 {f}")
    lines += ["", "## Priority Actions"]
    for i, a in enumerate(data.get("priority_actions", []), 1):
        badge = " ⭐ HIGH IMPACT" if i == 1 else ""
        lines.append(f"{i}. {a}{badge}")
    lines += [
        "",
        "## Key Quote",
        f'> "{data.get("key_quote", "")}"',
        "",
        "## Summary",
        data.get("summary", ""),
        "",
        "---",
        "_Generated by MerchantPulse · Built with Claude AI_",
    ]
    return "\n".join(lines)


# ── Run analysis ───────────────────────────────────────────────────────────────
if analyze_clicked:
    reviews_to_analyze = active_reviews.strip()

    if not reviews_to_analyze:
        st.warning("⚠️ Please paste at least one review or upload a CSV before analyzing.")
    else:
        review_count = len([r for r in reviews_to_analyze.splitlines() if r.strip()])
        with st.spinner("🤖 Analyzing with Claude AI — this takes about 5 seconds…"):
            try:
                result = call_claude(reviews_to_analyze, product_name or "")
            except ValueError as e:
                st.error(str(e))
                result = None
            except anthropic.APIError as e:
                st.error(f"Claude API error: {e}. Please check your API key and try again.")
                result = None
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                result = None

        if result:
            if result["ok"]:
                data = result["data"]
                render_results(data, review_count)

                st.markdown("<br>", unsafe_allow_html=True)
                md_report = build_markdown_report(data, product_name or "")
                st.download_button(
                    label="⬇️ Download Report (.md)",
                    data=md_report,
                    file_name="merchantpulse_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            else:
                st.warning("Claude returned a response but it wasn't valid JSON. Showing raw output:")
                st.code(result["raw"], language="text")
                st.download_button(
                    label="⬇️ Download Raw Response",
                    data=result["raw"],
                    file_name="merchantpulse_raw.txt",
                    mime="text/plain",
                )
