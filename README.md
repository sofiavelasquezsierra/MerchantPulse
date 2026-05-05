# MerchantPulse

**Turn customer reviews into product decisions — in seconds.**

![MerchantPulse Demo](screenshot.png)

---

## The Problem

Shopify merchants receive hundreds of product reviews but have no easy way to extract actionable insights. Reading reviews manually is time-consuming. Existing tools give sentiment scores but not product direction. Merchants end up guessing what to build next.

## The Solution

MerchantPulse uses AI to analyze product reviews and output a structured product brief: what's broken, what customers want, and what to prioritize — in plain English.

**Built for:** Shopify merchants with 50+ product reviews who want data-driven product decisions without hiring an analyst.

---

## What It Does

- Analyzes any number of product reviews (paste or CSV upload)
- Identifies top pain points with frequency estimates
- Surfaces feature requests directly from customer language
- Prioritizes actions by impact
- Exports a shareable Markdown report

---

## Demo

[Live app — Streamlit Community Cloud](#) *(add link after deploying)*

---

## Product Decisions I Made

> This section explains the product thinking behind key design choices.

**Why structured JSON output, not free text?**
Merchants need to act on insights, not read essays. Structured output maps directly to product decisions: pain points go to the bug backlog, feature requests go to the roadmap. A structured schema also makes it trivial to extend the app — adding a trend chart or Notion export becomes a data transformation, not a parsing problem.

**Why prioritized actions instead of a full list?**
Overwhelm kills action. Three priority recommendations force the model to make tradeoffs — which is what a product manager does. Limiting to three makes the output feel like a decision, not a dump.

**Why include a "key quote"?**
Data without a human voice doesn't move people. The key quote gives merchants something to share in a Slack thread or investor update that makes the insight real. A percentage is forgettable. A customer's actual words stick.

**Why a sentiment bar instead of just numbers?**
Visual proportion is processed faster than text. The color-coded bar lets merchants see at a glance whether their product is in trouble or in good shape — before reading a single word.

**What I'd build next:**
1. **Trend tracking over time** — upload reviews from multiple months and see how sentiment shifts after a product change or support improvement.
2. **Competitor comparison** — analyze reviews from a competitor's product to find their gaps and your opportunity.
3. **Shopify API integration** — pull reviews directly via the Shopify Admin API instead of copy-paste, making the workflow zero-friction.

---

## Technical Details

| | |
|---|---|
| **Stack** | Python, Streamlit, Anthropic Claude API |
| **Model** | claude-sonnet-4-6 |
| **Deployment** | Streamlit Community Cloud |
| **Auth** | API key via environment variable |
| **Storage** | Stateless — no database, no user data retained |

---

## Setup

```bash
git clone https://github.com/sofiavelasquezsierra/merchantpulse
cd merchantpulse
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
streamlit run main.py
```

Get an Anthropic API key at [console.anthropic.com](https://console.anthropic.com).

---

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (must be public or connected to your Streamlit account).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your repo, set the main file to `main.py`.
4. Under **Advanced settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
5. Click **Deploy**. Live in ~60 seconds.

---

## About

Built by **Sofia Velasquez Sierra** — MS Biomedical Engineering at CMU. I build ML systems that turn noisy data into decisions. MerchantPulse applies that same approach to e-commerce: take unstructured customer signal, extract structured insight, and make it actionable.

[LinkedIn](https://linkedin.com/in/sofia-velasquez) · [GitHub](https://github.com/sofiavelasquezsierra)
