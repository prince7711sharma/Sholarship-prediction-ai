# Scholarship Predictor AI

An AI-powered scholarship prediction and recommendation engine. This application helps students find scholarship opportunities using advanced LLM analysis and web search capabilities.

## Features

- **AI Prediction**: Evaluates student profiles and predicts scholarship eligibility.
- **Search Integration**: Uses Tavily for real-time scholarship search.
- **Modern UI**: A clean, responsive interface for easy interaction.
- **Production Ready**: Configured for deployment on Render.

## Tech Stack

- **Backend**: FastAPI, Gunicorn, Uvicorn
- **AI**: Groq (LLM), Tavily (Search API)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd scholarship-predictor-ai
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate      # Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Deployment on Render

This project is ready for deployment on Render.

1. **Connect your GitHub repository** to Render.
2. **Select Web Service**.
3. **Configure Build & Start Commands**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
4. **Environment Variables**: Add `GROQ_API_KEY` and `TAVILY_API_KEY` in the Render dashboard.

## License

MIT
