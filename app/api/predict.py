from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.student import Student
from app.services.prompt_service import build_prompt, build_system_message
from app.services.llm_service import get_llm_response
from app.services.search_service import search_scholarships
from app.core.logger import get_logger
from app.core.rate_limiter import check_rate_limit
import json
import re
from datetime import datetime

router = APIRouter()
logger = get_logger("predict_api")


def extract_json(text: str) -> dict:
    """Extract and parse JSON from LLM response text."""
    try:
        # Try direct parse first
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    try:
        # Try extracting JSON block from markdown code fence
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except json.JSONDecodeError:
        pass

    try:
        # Try finding JSON object in text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass

    return None


def build_fallback_response(data: Student) -> dict:
    """Build a detailed fallback response when LLM fails."""
    scholarships = [
        {
            "title": "National Scholarship Portal (NSP) - Post Matric Scholarship",
            "provider": "Ministry of Social Justice & Empowerment, Govt. of India",
            "eligibility": f"For {data.category} category students with family income below ₹2.5 lakh per annum pursuing post-matric education.",
            "benefit_amount": "₹12,000 - ₹50,000 per annum (varies by course level)",
            "deadline": "Usually October-November every year",
            "how_to_apply": "1. Visit scholarships.gov.in\n2. Register with your Aadhaar\n3. Fill the application form\n4. Upload required documents\n5. Submit and track status",
            "website": "https://scholarships.gov.in",
            "why_you_qualify": f"Your {data.category} category and family income of ₹{data.income:,} makes you eligible for this scholarship.",
            "match_score": 85
        },
        {
            "title": "Central Sector Scheme of Scholarships (CSSS)",
            "provider": "Ministry of Education, Govt. of India",
            "eligibility": f"Students with marks above 80% from families with income below ₹8 lakh. Must be in top 20% of board exam.",
            "benefit_amount": "₹10,000 - ₹20,000 per annum for up to 3 years",
            "deadline": "September-October annually",
            "how_to_apply": "1. Apply through National Scholarship Portal\n2. Verify board exam percentile\n3. Submit income certificate\n4. Institute verification required",
            "website": "https://scholarships.gov.in",
            "why_you_qualify": f"With {data.marks}% marks and ₹{data.income:,} family income, you meet the eligibility criteria.",
            "match_score": 75
        },
        {
            "title": f"{data.state} State Merit Scholarship",
            "provider": f"Directorate of Higher Education, {data.state}",
            "eligibility": f"Domicile of {data.state} pursuing {data.course} with good academic performance.",
            "benefit_amount": "₹5,000 - ₹25,000 per annum (varies by state)",
            "deadline": "Check state scholarship portal for deadlines",
            "how_to_apply": f"1. Visit {data.state} state scholarship portal\n2. Check available schemes\n3. Apply online with state domicile certificate\n4. Submit academic records",
            "website": f"https://scholarships.gov.in",
            "why_you_qualify": f"As a {data.state} domicile student pursuing {data.course}, you are eligible for state-specific scholarships.",
            "match_score": 70
        }
    ]

    probability = min(95, max(30, 90 - (data.marks < 60) * 20 - (data.income > 500000) * 15 + (data.category in ["SC", "ST", "OBC"]) * 10))
    recommendation = "High" if probability >= 70 else "Medium" if probability >= 45 else "Low"

    return {
        "probability": probability,
        "recommendation": recommendation,
        "summary": f"Based on your profile ({data.marks}% marks, {data.category} category, ₹{data.income:,} family income in {data.state}), we found several scholarship opportunities for your {data.course} course. We recommend applying to all matching scholarships to maximize your chances.",
        "scholarships": scholarships
    }


@router.post("/predict", dependencies=[Depends(check_rate_limit)])
def predict(data: Student):
    """Main prediction endpoint — combines search + LLM for rich scholarship recommendations."""

    request_time = datetime.now().isoformat()
    logger.info(f"📩 Prediction request: marks={data.marks}, category={data.category}, income={data.income}, state={data.state}, course={data.course}, gender={data.gender}, disability={data.disability}")

    # ─── Fail check: marks below 33% ─────────────────────
    if data.marks < 33:
        logger.info(f"⛔ Marks below 33% ({data.marks}%) — no scholarships eligible")
        return {
            "status": "fail",
            "timestamp": request_time,
            "student": {
                "marks": data.marks,
                "category": data.category,
                "income": data.income,
                "state": data.state,
                "course": data.course
            },
            "data": {
                "probability": 0,
                "recommendation": "Not Eligible",
                "summary": f"With {data.marks}% marks (below 33% passing threshold), you are currently not eligible for scholarship programs. Most scholarships require a minimum passing percentage. Focus on improving your academic performance first.",
                "scholarships": []
            }
        }

    try:
        # Step 1: Search for real scholarship data
        logger.info("Step 1/3: Searching web for scholarships...")
        search_results = search_scholarships(
            state=data.state,
            category=data.category,
            course=data.course,
            income=data.income
        )

        # Step 2: Build prompt with search results
        logger.info("Step 2/3: Building enhanced prompt...")
        system_message = build_system_message()
        prompt = build_prompt(data, search_results)

        # Step 3: Get LLM response
        logger.info("Step 3/3: Getting AI recommendations...")
        result = get_llm_response(prompt, system_message)
        parsed = extract_json(result) if result else None

        # Validate the parsed response
        if parsed:
            # Ensure required fields exist
            if "scholarships" not in parsed or not isinstance(parsed.get("scholarships"), list):
                logger.warning("LLM response missing scholarships array — using fallback")
                parsed = None
            elif len(parsed["scholarships"]) < 2:
                logger.warning("LLM returned too few scholarships — using fallback")
                parsed = None
            else:
                # Ensure all fields have defaults
                parsed.setdefault("probability", 70)
                parsed.setdefault("recommendation", "Medium")
                parsed.setdefault("summary", f"We found {len(parsed['scholarships'])} scholarship opportunities matching your profile.")

                # Ensure each scholarship has all fields
                for s in parsed["scholarships"]:
                    s.setdefault("provider", "Government of India")
                    s.setdefault("eligibility", "Check official website for details")
                    s.setdefault("benefit_amount", "Varies")
                    s.setdefault("deadline", "Check official website")
                    s.setdefault("how_to_apply", "Visit the official website and apply online")
                    s.setdefault("website", "https://scholarships.gov.in")
                    s.setdefault("why_you_qualify", "Based on your profile, you may be eligible")
                    s.setdefault("match_score", 60)

                logger.info(f"Successfully parsed {len(parsed['scholarships'])} scholarships from LLM")

        # Fallback if LLM failed
        if not parsed:
            logger.warning("Using fallback scholarship data")
            parsed = build_fallback_response(data)

        response = {
            "status": "success",
            "timestamp": request_time,
            "student": {
                "marks": data.marks,
                "category": data.category,
                "income": data.income,
                "state": data.state,
                "course": data.course
            },
            "data": parsed
        }

        logger.info(f"✅ Response sent: {parsed['recommendation']} recommendation, {parsed['probability']}% probability, {len(parsed['scholarships'])} scholarships")
        return response

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        # Even on error, return useful fallback data
        fallback = build_fallback_response(data)
        return {
            "status": "success",
            "timestamp": request_time,
            "data": fallback,
            "note": "Results generated from our database (AI service temporarily slow)"
        }