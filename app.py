from flask import Flask, request, jsonify, send_from_directory
from google import genai
from dotenv import load_dotenv
import os
import json
import re

# ============================================================
# LIFEBridge AI - Backend
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

app = Flask(__name__, static_folder="public")


# ============================================================
# LIFEBridge SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are LifeBridge AI, a structured real-world decision-support assistant.

Your job is NOT to simply give advice.

Your job is to transform a messy real-world situation into a clear,
responsible action plan using four stages:

UNDERSTAND → VERIFY → PRIORITIZE → ACT


========================
1. YOUR ROLE
========================

Act as a careful situation analyst and action-planning assistant.

You must:
- Understand what the user is actually dealing with.
- Separate known information from assumptions.
- Identify information that may need verification.
- Determine the urgency and priority.
- Give practical next steps.
- Select the single most useful next action.
- Explain why that action should come first.


========================
2. INPUT CONTEXT
========================

The user may provide:

Situation:
A messy description of their problem or situation.

Context type:
Education, Technology, Travel, Finance, Health, Work, Personal,
or another category.

Detail level:
Quick, Balanced, or Step-by-Step.

Additional context:
Optional information that may help understand the situation.


========================
3. CORE TASK
========================

Analyze the user's situation and produce an Action Card.

The analysis must answer:

1. What is happening?
2. What important information is already known?
3. What information is actually supported by the user's input?
4. What information is uncertain or needs confirmation?
5. How important or urgent is the situation?
6. What practical actions can the user take?
7. What should they do FIRST?
8. Why should that action come first?


========================
4. FACT VS UNCERTAINTY RULE
========================

Never invent facts.

Use:

FACTS:
Information directly stated or clearly supported by the user's input.

SUPPORTED:
Reasonable conclusions that follow directly from the provided information.

NEEDS VERIFICATION:
Information that is unknown, uncertain, time-sensitive, location-specific,
or would require checking an external source.

Never claim that you verified something unless the user actually provided
the verified information.

If something cannot be confirmed, clearly place it in
"needs_verification".


========================
5. PRIORITY RULE
========================

Choose exactly ONE priority:

Low
Medium
High
Urgent

Use these meanings:

LOW:
The situation is useful to address but does not require immediate action.

MEDIUM:
The situation should be handled soon to avoid unnecessary problems.

HIGH:
There is a significant deadline, risk, consequence, or time pressure.

URGENT:
There may be an immediate safety, health, security, or serious-risk issue
requiring prompt professional or emergency assistance when appropriate.

Do not label ordinary inconvenience as Urgent.


========================
6. ACTION RULE
========================

Actions must be:

- Practical
- Specific
- Safe
- Relevant to the user's situation
- Ordered logically

Avoid vague actions such as:
"Be careful."
"Try harder."
"Think about it."

Instead give concrete actions that the user can actually perform.


========================
7. NEXT BEST ACTION
========================

Choose ONE action as the "next_best_action".

It must be the most useful immediate step.

The action should:
- Reduce uncertainty, OR
- Reduce risk, OR
- Move the user meaningfully toward solving the situation.

Then explain the reasoning in "why_action".


========================
8. CONFIDENCE
========================

Return a confidence score from 0 to 100.

The score represents confidence in the QUALITY OF THE ANALYSIS,
not certainty that every fact in the real world is correct.

Use lower confidence when important information is missing.

Do not use confidence as a replacement for verification.


========================
9. SAFETY BOUNDARIES
========================

For health-related situations:
- Do not diagnose diseases.
- Do not prescribe medication.
- Do not pretend to replace a doctor.
- Clearly recommend qualified professional help when appropriate.
- If the situation appears potentially dangerous or urgent,
  recommend appropriate emergency/professional assistance.

For safety-critical situations:
- Do not encourage risky actions.
- Prefer safe escalation and professional help when appropriate.

For financial or legal situations:
- Do not present uncertain information as guaranteed.
- Identify important information that should be verified.


========================
10. RESPONSE QUALITY CHECK
========================

Before returning the answer, internally check:

A. Did I understand the actual situation?
B. Did I avoid inventing facts?
C. Did I separate supported information from uncertainty?
D. Is the priority reasonable?
E. Are the actions practical?
F. Is there exactly one clear next best action?
G. Does the explanation actually justify that action?
H. Is confidence consistent with the available information?
I. Did I follow the requested detail level?
J. Is the response safe and responsible?


========================
11. REQUIRED JSON OUTPUT
========================

Return ONLY valid JSON.

Do not use Markdown.
Do not use code fences.
Do not add explanations outside the JSON.

Use exactly this structure:

{
  "priority": "Low | Medium | High | Urgent",
  "priority_reason": "Short explanation of why this priority was selected.",
  "confidence": 0,
  "situation_summary": "Clear summary of the user's situation.",
  "facts": [
    "Important fact from the user's input."
  ],
  "verified": [
    "Information that is directly supported by the user's input."
  ],
  "needs_verification": [
    "Information that is uncertain or should be confirmed."
  ],
  "actions": [
    "First practical action.",
    "Second practical action.",
    "Third practical action."
  ],
  "next_action": "The single most useful immediate action.",
  "why_action": "Why this action should be done first."
}

Additional rules:

- confidence must be an integer from 0 to 100.
- priority must be exactly Low, Medium, High, or Urgent.
- Every array must contain useful information when possible.
- Do not fabricate sources.
- Do not claim external verification.
- Keep the response concise but useful.
"""


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_json_response(text):
    """
    Removes common Markdown formatting if Gemini accidentally
    wraps JSON inside a code block.
    """

    if not text:
        return ""

    text = text.strip()

    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return text.strip()


def safe_string(value, default=""):
    """
    Convert a value into a clean string.
    """

    if value is None:
        return default

    return str(value).strip()


def safe_list(value):
    """
    Convert a value into a clean list of strings.
    """

    if not isinstance(value, list):
        return []

    cleaned = []

    for item in value:
        if item is None:
            continue

        item = str(item).strip()

        if item:
            cleaned.append(item)

    return cleaned


def normalize_result(data):
    """
    Ensures the AI response always follows the expected structure.
    """

    if not isinstance(data, dict):
        data = {}

    priority = safe_string(data.get("priority"), "Medium")

    allowed_priorities = ["Low", "Medium", "High", "Urgent"]

    if priority not in allowed_priorities:
        priority = "Medium"

    confidence = data.get("confidence", 50)

    try:
        confidence = int(confidence)
    except (ValueError, TypeError):
        confidence = 50

    confidence = max(0, min(100, confidence))

    result = {
        "priority": priority,
        "priority_reason": safe_string(
            data.get("priority_reason"),
            "Priority is based on the information currently available."
        ),
        "confidence": confidence,
        "situation_summary": safe_string(
            data.get("situation_summary"),
            "The situation requires further understanding."
        ),
        "facts": safe_list(data.get("facts")),
        "verified": safe_list(data.get("verified")),
        "needs_verification": safe_list(data.get("needs_verification")),
        "actions": safe_list(data.get("actions")),
        "next_action": safe_string(
            data.get("next_action"),
            "Review the available information and identify the most important missing detail."
        ),
        "why_action": safe_string(
            data.get("why_action"),
            "This is the best first step because it helps clarify the situation."
        )
    }

    return result


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    return send_from_directory("public", "index.html")


@app.route("/style.css")
def style():
    return send_from_directory("public", "style.css")


@app.route("/script.js")
def script():
    return send_from_directory("public", "script.js")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "service": "LifeBridge AI",
        "status": "running",
        "gemini_configured": bool(GEMINI_API_KEY)
    })


# ============================================================
# MAIN AI ANALYSIS
# ============================================================

@app.route("/api/analyze", methods=["POST"])
def analyze():

    try:

        # ----------------------------------------------------
        # Check Gemini configuration
        # ----------------------------------------------------

        if not client:
            return jsonify({
                "success": False,
                "error": "Gemini API key is not configured."
            }), 500


        # ----------------------------------------------------
        # Read request
        # ----------------------------------------------------

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "success": False,
                "error": "No input data was received."
            }), 400


        situation = safe_string(data.get("situation"))

        context_type = safe_string(
            data.get("context_type"),
            "General"
        )

        detail_level = safe_string(
            data.get("detail_level"),
            "Balanced"
        )

        additional_context = safe_string(
            data.get("additional_context")
        )


        # ----------------------------------------------------
        # Validate situation
        # ----------------------------------------------------

        if not situation:

            return jsonify({
                "success": False,
                "error": "Please describe your situation first."
            }), 400


        if len(situation) > 5000:

            return jsonify({
                "success": False,
                "error": "Please keep the situation under 5000 characters."
            }), 400


        # ----------------------------------------------------
        # Build structured user input
        # ----------------------------------------------------

        user_prompt = f"""
Analyze this real-world situation using the LifeBridge framework.

========================
USER SITUATION
========================

{situation}

========================
CONTEXT TYPE
========================

{context_type}

========================
REQUESTED DETAIL LEVEL
========================

{detail_level}

========================
ADDITIONAL CONTEXT
========================

{additional_context if additional_context else "No additional context provided."}

========================
IMPORTANT
========================

Do not assume missing facts.

Clearly distinguish:
- facts
- supported information
- information needing verification

Then determine:
- priority
- practical actions
- one next best action
- why that action comes first

Return ONLY the required JSON structure.
"""


        # ----------------------------------------------------
        # Call Gemini
        # ----------------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": SYSTEM_PROMPT + "\n\n" + user_prompt
                        }
                    ]
                }
            ]
        )


        # ----------------------------------------------------
        # Read Gemini response
        # ----------------------------------------------------

        raw_text = getattr(response, "text", "")

        if not raw_text:

            return jsonify({
                "success": False,
                "error": "The AI returned an empty response."
            }), 500


        # ----------------------------------------------------
        # Clean response
        # ----------------------------------------------------

        cleaned_text = clean_json_response(raw_text)


        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        try:

            result_data = json.loads(cleaned_text)

        except json.JSONDecodeError:

            # Attempt to locate the JSON object if Gemini added
            # unexpected text around it.

            start = cleaned_text.find("{")
            end = cleaned_text.rfind("}")

            if start != -1 and end != -1 and end > start:

                possible_json = cleaned_text[start:end + 1]

                try:
                    result_data = json.loads(possible_json)

                except json.JSONDecodeError:

                    return jsonify({
                        "success": False,
                        "error": "The AI returned an invalid response format."
                    }), 500

            else:

                return jsonify({
                    "success": False,
                    "error": "The AI returned an invalid response format."
                }), 500


        # ----------------------------------------------------
        # Normalize result
        # ----------------------------------------------------

        result = normalize_result(result_data)


        # ----------------------------------------------------
        # Return final response
        # ----------------------------------------------------

        return jsonify({
            "success": True,
            **result
        })


    except Exception as e:

        print("LifeBridge error:", str(e))

        return jsonify({
            "success": False,
            "error": "Something went wrong while analyzing the situation. Please try again."
        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 3000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )