def build_system_message() -> str:
    """Build the system message for the LLM to control response behavior."""
    return """You are an Indian scholarship advisor AI. Respond ONLY in valid JSON. Provide accurate, actionable scholarship recommendations. Focus on scholarships the student is most likely to qualify for. Be concise."""


def build_prompt(data, search_results: str = "") -> str:
    """Build a rich, multi-section prompt combining student data and search results."""

    income_bracket = data.income_bracket
    gender_info = f"\nGender: {data.gender}" if data.gender else ""
    disability_info = f"\nPerson with Disability: Yes" if data.disability else ""

    search_section = ""
    if search_results:
        search_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 REAL-TIME SCHOLARSHIP DATA FROM WEB SEARCH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{search_results}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use the above search results to provide REAL, ACCURATE scholarship information.
Prioritize scholarships found in the search results but also add your own knowledge.
"""

    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 STUDENT PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Marks/Percentage: {data.marks}%
🏷️ Category: {data.category}
💰 Family Annual Income: ₹{data.income:,} ({income_bracket})
📍 State: {data.state}
📚 Course: {data.course}{gender_info}{disability_info}

{search_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 YOUR TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide EXACTLY 4 personalized scholarship recommendations with: name, provider, eligibility, amount, deadline, how to apply, website, why they qualify, and match_score.

Also provide: probability (0-100), recommendation (High/Medium/Low), and a 1-2 sentence summary.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 REQUIRED JSON FORMAT (respond ONLY with this JSON, nothing else):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "probability": <number 0-100>,
  "recommendation": "<High|Medium|Low>",
  "summary": "<Personalized 2-3 sentence summary for the student>",
  "scholarships": [
    {{
      "title": "<Full Scholarship Name>",
      "provider": "<Government body or organization name>",
      "eligibility": "<Detailed eligibility criteria>",
      "benefit_amount": "<₹ Amount or range>",
      "deadline": "<Application deadline or timeline>",
      "how_to_apply": "<Step-by-step application process>",
      "website": "<Official URL>",
      "why_you_qualify": "<Specific reason why THIS student qualifies>",
      "match_score": <number 0-100>
    }}
  ]
}}
"""