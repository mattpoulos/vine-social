import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import random
import streamlit as st

# --- OpenAI Client ---
client = OpenAI()

# --- Streamlit Page Config ---
st.set_page_config(page_title="Vine Social", page_icon="🍇", layout="centered")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        body {
            background-color: #FAF7F2;
        }
        .block-container {
            padding: 2rem 2rem;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Helvetica Neue', sans-serif;
            color: #2E2B27;
        }
        .stButton>button {
            background-color: #E4D8C4;
            color: #2E2B27;
            border: none;
            border-radius: 10px;
            padding: 10px 24px;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #d6c5aa;
            color: #2E2B27;
        }
    </style>
""", unsafe_allow_html=True)

# --- App Header ---
st.title("Vine Social")
st.markdown("Helping local businesses thrive with AI-powered social strategy.")
st.markdown("---")

# --- Business Info Form ---
st.subheader("Generate a Post Idea")

with st.form("post_form"):
    website_url = st.text_input("Business Website URL")
    target_audience = st.text_input("Describe your ideal local customer")
    brand_voice = st.text_input("Describe your brand's personality (e.g., fun, warm, educational)")
    special_offers = st.text_input("Any promotions, events, or news to highlight?")
    platform_preference = st.text_input("Preferred social media platform (Instagram, TikTok, etc.)")
    personal_goal = st.text_input("What is your goal for this post? (e.g. bookings, brand awareness, sales)")
    submitted = st.form_submit_button("Generate Post Idea")

# --- Scrape Website ---
def scrape_website(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]
    except requests.exceptions.RequestException as e:
        return f"Error scraping site: {e}"

# --- Summarize Website Content ---
def summarize_website_content(raw_text):
    prompt = f"""
You are a branding strategist. Summarize the key details of this local business based on the following website text.

Include:
- What the business does
- Its tone or brand personality
- Any standout services or promotions
Keep it under 100 words.

Website content:
{raw_text}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing website content: {e}"

# --- Campaign Insights ---
campaign_insights = """
🍻 Food & Beverage:
- UGC showing people enjoying the product
- Limited-time menu drops
- Behind-the-scenes of prep or baking
- Local collabs (coffee shop x bakery)

💇 Beauty & Wellness:
- Before & after transformations
- Staff spotlights
- Customer testimonials
- Service “how it works” Reels

💼 Retail (Clothing, Home, Gifts):
- Try-ons / in-store hauls
- Community shoutouts (local makers)
- Flash sales or limited drops
- Lifestyle flatlays with product tags

🛠 Service-Based Businesses:
- Time-lapse or before/after
- Educational tips for locals
- Local reviews / video testimonials
- Problem + solution storytelling

🏫 Education / Coaching / Kids Services:
- Client wins or student spotlights
- Tips for parents / students
- Event recaps
- Mission-driven storytelling
"""

# --- Generate Post Idea ---
def generate_post_idea(summarized_website, business_info):
    campaign_types = """
    - Educational
    - Problem vs Solution
    - Results
    - Storytelling
    - Community Engagement
    """
    insights = campaign_insights.strip().split("\n\n")
    random.shuffle(insights)
    random_campaign_insights = "\n\n".join(insights[:3])

    prompt = f"""
You're a top-tier social media strategist for local businesses.

Based on the business summary and goals below, choose the most suitable campaign type from the following list:
{campaign_types}

Then, create **one complete social media campaign post** that includes:
1. Post Type — e.g. Instagram Reel, Carousel, Story, etc.
2. A single Best Performing Visual — clearly described scene.
3. A full, scroll-stopping caption (max 250 characters).

This must be:
- Unified as one idea
- Based on best-performing campaign styles for the business's niche
- Designed to drive engagement or conversion
- Easy to use for a local business owner

Business Summary:
{summarized_website}

Campaign Insights:
{random_campaign_insights}

Goal: {business_info['business_goals']}
Target Audience: {business_info['target_audience']}
Brand Voice: {business_info['brand_voice']}
Special Offers / News: {business_info['special_offers']}
Preferred Platform: {business_info['platform_preference']}
User’s Personal Goal for This Post: {business_info['personal_goal']}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating post idea: {e}"

# --- Run Generation ---
if submitted and website_url:
    with st.spinner("Scraping website and generating idea..."):
        site_content = scrape_website(website_url)

        if "Error" in site_content:
            st.error(site_content)
        else:
            summary = summarize_website_content(site_content)
            business_info = {
                "target_audience": target_audience,
                "brand_voice": brand_voice,
                "business_goals": "Drive social media engagement",
                "special_offers": special_offers,
                "platform_preference": platform_preference,
                "personal_goal": personal_goal,
            }
            post_idea = generate_post_idea(summary, business_info)
            st.success("✅ Here's your social media post idea:")
            st.markdown(f"**Business Summary:**\n{summary}")
            st.markdown(f"**User’s Goal for This Post:** {personal_goal}")
            st.markdown("---")
            st.markdown(post_idea)

# --- Footer ---
st.markdown("---")
st.caption("Built with 🤍 by Vine Social")
