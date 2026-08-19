🔍 BizLens AI

AI-powered business intelligence from Google Maps reviews.

BizLens AI analyzes a business's Google Maps presence and customer reviews to provide actionable insights, business health scoring, and AI-powered recommendations.

✨ Features
🔎 Analyze businesses using a Google Maps URL
⭐ Google rating & review analysis
🧠 AI-powered customer sentiment analysis
📊 Business Health Score (0–100)
💡 Actionable business recommendations
🚀 Personalized 30-day improvement plan
💬 AI Business Consultant
📈 Interactive analytics dashboard
🛠️ Tech Stack
Frontend: Streamlit
Backend: Python
AI: Groq + Llama 3.3 70B
Data: Google Places API
Visualization: Plotly
⚙️ How It Works
Google Maps URL
       ↓
Google Places API
       ↓
Business & Reviews
       ↓
AI Analysis
       ↓
Health Score + Insights
       ↓
Recommendations + 30-Day Plan

🚀 Installation

Clone the repository:

git clone https://github.com/nithinXreddy/Business-intel-bizlens-AI-.git
cd Business-intel-bizlens-AI-


Install dependencies:

pip install -r requirements.txt


Configure your API keys:

PLACES_API_KEY=your_google_places_api_key
GROQ_API_KEY=your_groq_api_key


Run the application:

streamlit run app.py


Then open the URL shown by Streamlit in your browser.

📁 Project Structure
Business-intel-bizlens-AI/
│
├── app.py            # Streamlit dashboard
├── analyzer.py       # AI analysis & recommendations
├── scraper.py        # Google Places data retrieval
├── requirements.txt  # Dependencies
└── .gitignore

📊 Health Score

BizLens AI calculates a score from 0–100 using:

Google Rating
Customer Sentiment
Review Volume
Complaint Severity

The score helps identify whether a business is performing well or needs improvement.

🔮 Future Improvements
Competitor analysis
Historical performance tracking
Automated review responses
PDF reports
User authentication
Database integration
👨‍💻 Author

Nithin Reddy

GitHub: @nithinXreddy

⭐ If you find BizLens AI useful, consider starring the repository!
