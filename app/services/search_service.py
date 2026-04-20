import os
from dotenv import load_dotenv
from app.core.logger import get_logger
from app.core.config import TAVILY_API_KEY, SEARCH_MAX_RESULTS

load_dotenv()
logger = get_logger("search_service")


def search_scholarships(state: str, category: str, course: str, income: int = 0) -> str:
    """
    Search for real scholarship data using Tavily API.
    Returns formatted search results with titles and snippets.
    """
    if not TAVILY_API_KEY:
        logger.warning("No Tavily API key configured — using fallback data")
        return _get_fallback_data(state, category, course, income)

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)

        # Build a detailed search query
        income_label = ""
        if income <= 250000:
            income_label = "low income economically weaker"
        elif income <= 500000:
            income_label = "middle income"

        query = f"scholarships for {category} category students in {state} for {course} {income_label} India 2025 2026"
        logger.info(f"Searching: {query}")

        res = client.search(
            query=query,
            max_results=SEARCH_MAX_RESULTS,
            search_depth="advanced"
        )

        # Build rich results with title + content
        results = []
        for r in res.get("results", []):
            title = r.get("title", "Unknown")
            content = r.get("content", "")
            url = r.get("url", "")
            results.append(f"📌 {title}\n   {content}\n   🔗 {url}")

        if results:
            output = "\n\n".join(results)
            logger.info(f"Found {len(results)} search results")
            return output
        else:
            logger.warning("No search results found — using fallback")
            return _get_fallback_data(state, category, course, income)

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return _get_fallback_data(state, category, course, income)


def _get_fallback_data(state: str, category: str, course: str, income: int) -> str:
    """Provide structured fallback scholarship data when search fails."""
    fallback = []

    fallback.append(f"📌 National Scholarship Portal (NSP)\n   Government of India scholarships for {category} category students. Multiple schemes available including Pre-Matric and Post-Matric scholarships.\n   🔗 https://scholarships.gov.in")

    if category in ["SC", "ST"]:
        fallback.append(f"📌 Post Matric Scholarship for {category} Students\n   Ministry of Social Justice scholarship for {category} students pursuing higher education. Covers tuition, maintenance allowance.\n   🔗 https://scholarships.gov.in")

    if category == "OBC":
        fallback.append(f"📌 Post Matric Scholarship for OBC Students\n   For OBC students with family income below ₹1 lakh. Covers non-refundable fees.\n   🔗 https://scholarships.gov.in")

    if income <= 250000:
        fallback.append(f"📌 Central Sector Scheme of Scholarships\n   For students from families with income below ₹2.5 lakh. ₹10,000-₹20,000 per annum for various courses.\n   🔗 https://scholarships.gov.in")

    fallback.append(f"📌 {state} State Scholarship Scheme\n   State government scholarships for students of {state} pursuing {course}. Various schemes available based on merit and income.\n   🔗 Check your state scholarship portal")

    fallback.append(f"📌 Merit-cum-Means Scholarship\n   For meritorious students from economically weaker sections. Applicable for professional and technical courses.\n   🔗 https://scholarships.gov.in")

    return "\n\n".join(fallback)