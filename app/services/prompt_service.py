def build_system_message() -> str:
    """Build the system message for the LLM to control response behavior."""
    return "You are an Indian scholarship advisor AI. Respond ONLY in valid JSON. Provide accurate, actionable recommendations. Be concise."


def build_prompt(data, search_results: str = "") -> str:
    """Build an optimized prompt combining student data and search results."""

    income_bracket = data.income_bracket
    gender_info = f"\nGender: {data.gender}" if data.gender else ""
    disability_info = f"\ndisability: Yes" if data.disability else ""

    search_section = ""
    if search_results:
        search_section = f"\nREAL-TIME DATA:\n{search_results}\nUse this search data to provide real scholarships. Prioritize them."

    return f"""STUDENT PROFILE:
- Marks: {data.marks}%
- Category: {data.category}
- Income: ₹{data.income:,} ({income_bracket})
- State: {data.state}
- Course: {data.course}{gender_info}{disability_info}

{search_section}

TASK: Provide 4 personalized scholarship recommendations.
Include: probability (0-100), recommendation (High/Medium/Low), and a brief summary.

JSON FORMAT:
{{
  "probability": 85,
  "recommendation": "High",
  "summary": "Short summary here...",
  "scholarships": [
    {{
      "title": "Name",
      "provider": "Body",
      "eligibility": "Criteria",
      "benefit_amount": "Amount",
      "deadline": "Date",
      "how_to_apply": "Steps",
      "website": "URL",
      "why_you_qualify": "Reason",
      "match_score": 90
    }}
  ]
}}
"""