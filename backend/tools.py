"""
LangGraph Tools for HCP CRM Agent
Tools:
1. log_interaction     - Extract & log interaction from natural language
2. edit_interaction    - Edit specific fields of logged interaction
3. get_hcp_details     - Fetch HCP info from the database
4. suggest_followup    - AI-generate follow-up action recommendations
5. summarize_interaction - Summarize/format interaction notes
"""

import json
import re
from datetime import datetime
from typing import Optional, Any
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from database import SessionLocal, Interaction, HCP


def _get_db() -> Session:
    return SessionLocal()


@tool
def log_interaction(
    hcp_name: str,
    interaction_type: Optional[str] = "Meeting",
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[list] = None,
    samples_distributed: Optional[list] = None,
    sentiment: Optional[str] = "Neutral",
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
) -> dict:
    """
    Log a new HCP interaction to the database with all extracted details.
    Use this tool to create a new interaction record when the user describes meeting an HCP.
    Extract all relevant information from the user's natural language description.
    """
    db = _get_db()
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        if not time:
            time = datetime.now().strftime("%H:%M")

        interaction = Interaction(
            hcp_name=hcp_name,
            interaction_type=interaction_type,
            date=date,
            time=time,
            attendees=attendees,
            topics_discussed=topics_discussed,
            materials_shared=materials_shared or [],
            samples_distributed=samples_distributed or [],
            sentiment=sentiment,
            outcomes=outcomes,
            follow_up_actions=follow_up_actions,
            ai_suggested_followups=[],
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return {
            "success": True,
            "message": f"Interaction with {hcp_name} logged successfully.",
            "interaction_id": interaction.id,
            "form_data": {
                "id": interaction.id,
                "hcp_name": interaction.hcp_name,
                "interaction_type": interaction.interaction_type,
                "date": interaction.date,
                "time": interaction.time,
                "attendees": interaction.attendees,
                "topics_discussed": interaction.topics_discussed,
                "materials_shared": interaction.materials_shared,
                "samples_distributed": interaction.samples_distributed,
                "sentiment": interaction.sentiment,
                "outcomes": interaction.outcomes,
                "follow_up_actions": interaction.follow_up_actions,
                "ai_suggested_followups": interaction.ai_suggested_followups,
            },
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error logging interaction: {str(e)}"}
    finally:
        db.close()


@tool
def edit_interaction(
    interaction_id: int,
    hcp_name: Optional[str] = None,
    interaction_type: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    attendees: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    materials_shared: Optional[list] = None,
    samples_distributed: Optional[list] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
) -> dict:
    """
    Edit specific fields of an existing interaction. Only the fields provided (non-None) will be updated.
    Use this when the user wants to correct or update specific details of a logged interaction.
    The interaction_id must be provided to identify which record to update.
    """
    db = _get_db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not interaction:
            return {"success": False, "message": f"Interaction with ID {interaction_id} not found."}

        updated_fields = []
        if hcp_name is not None:
            interaction.hcp_name = hcp_name
            updated_fields.append("hcp_name")
        if interaction_type is not None:
            interaction.interaction_type = interaction_type
            updated_fields.append("interaction_type")
        if date is not None:
            interaction.date = date
            updated_fields.append("date")
        if time is not None:
            interaction.time = time
            updated_fields.append("time")
        if attendees is not None:
            interaction.attendees = attendees
            updated_fields.append("attendees")
        if topics_discussed is not None:
            interaction.topics_discussed = topics_discussed
            updated_fields.append("topics_discussed")
        if materials_shared is not None:
            interaction.materials_shared = materials_shared
            updated_fields.append("materials_shared")
        if samples_distributed is not None:
            interaction.samples_distributed = samples_distributed
            updated_fields.append("samples_distributed")
        if sentiment is not None:
            interaction.sentiment = sentiment
            updated_fields.append("sentiment")
        if outcomes is not None:
            interaction.outcomes = outcomes
            updated_fields.append("outcomes")
        if follow_up_actions is not None:
            interaction.follow_up_actions = follow_up_actions
            updated_fields.append("follow_up_actions")

        interaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(interaction)

        return {
            "success": True,
            "message": f"Updated fields: {', '.join(updated_fields)}",
            "interaction_id": interaction.id,
            "form_data": {
                "id": interaction.id,
                "hcp_name": interaction.hcp_name,
                "interaction_type": interaction.interaction_type,
                "date": interaction.date,
                "time": interaction.time,
                "attendees": interaction.attendees,
                "topics_discussed": interaction.topics_discussed,
                "materials_shared": interaction.materials_shared,
                "samples_distributed": interaction.samples_distributed,
                "sentiment": interaction.sentiment,
                "outcomes": interaction.outcomes,
                "follow_up_actions": interaction.follow_up_actions,
                "ai_suggested_followups": interaction.ai_suggested_followups,
            },
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Error editing interaction: {str(e)}"}
    finally:
        db.close()


@tool
def get_hcp_details(hcp_name: str) -> dict:
    """
    Retrieve details about a Healthcare Professional (HCP) from the database by name.
    Use this to look up HCP information such as specialty, hospital, city, email, and phone.
    This is useful for auto-populating fields or verifying HCP identity.
    """
    db = _get_db()
    try:
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name}%")).first()
        if hcp:
            return {
                "success": True,
                "hcp": {
                    "id": hcp.id,
                    "name": hcp.name,
                    "specialty": hcp.specialty,
                    "hospital": hcp.hospital,
                    "city": hcp.city,
                    "email": hcp.email,
                    "phone": hcp.phone,
                },
                "message": f"Found HCP: {hcp.name} ({hcp.specialty}) at {hcp.hospital}",
            }
        else:
            # Return all HCPs for reference
            all_hcps = db.query(HCP).all()
            names = [h.name for h in all_hcps]
            return {
                "success": False,
                "message": f"HCP '{hcp_name}' not found. Available HCPs: {', '.join(names)}",
            }
    except Exception as e:
        return {"success": False, "message": f"Error fetching HCP: {str(e)}"}
    finally:
        db.close()


@tool
def suggest_followup(
    interaction_id: int,
    topics_discussed: str,
    sentiment: str,
    hcp_name: str,
    outcomes: Optional[str] = None,
) -> dict:
    """
    Generate AI-powered follow-up action suggestions based on the interaction details.
    Use this after logging an interaction to provide intelligent next-step recommendations.
    Updates the ai_suggested_followups field in the database.
    """
    suggestions = []

    sentiment_lower = sentiment.lower() if sentiment else "neutral"
    topics_lower = topics_discussed.lower() if topics_discussed else ""
    outcomes_lower = outcomes.lower() if outcomes else ""

    # Context-aware suggestions based on sentiment
    if sentiment_lower == "positive":
        suggestions.append(f"Schedule a follow-up meeting with {hcp_name} within 2 weeks to maintain momentum")
        suggestions.append("Send a thank-you note and product efficacy summary document")
    elif sentiment_lower == "negative":
        suggestions.append(f"Escalate concerns raised by {hcp_name} to medical affairs team")
        suggestions.append("Prepare a detailed response document addressing objections raised")
        suggestions.append(f"Request supervisor support for next visit to {hcp_name}")
    else:
        suggestions.append(f"Schedule a follow-up call with {hcp_name} in 1 week to assess interest")

    # Topic-based suggestions
    if "sample" in topics_lower or "sample" in outcomes_lower:
        suggestions.append("Submit sample distribution report to compliance team")
    if "brochure" in topics_lower or "material" in topics_lower:
        suggestions.append("Verify receipt and review of shared materials in next visit")
    if "trial" in topics_lower or "study" in topics_lower:
        suggestions.append("Send latest clinical trial data and peer-reviewed publications")
    if "competitor" in topics_lower:
        suggestions.append("Prepare competitive analysis document for next interaction")
    if "advisory" in outcomes_lower or "advisory" in topics_lower:
        suggestions.append(f"Add {hcp_name} to the advisory board invitation list")

    # Always add a CRM update suggestion
    suggestions.append("Update CRM with all interaction notes within 24 hours")

    # Limit to top 4 most relevant suggestions
    suggestions = suggestions[:4]

    db = _get_db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if interaction:
            interaction.ai_suggested_followups = suggestions
            db.commit()

        return {
            "success": True,
            "message": f"Generated {len(suggestions)} follow-up suggestions for interaction with {hcp_name}",
            "suggestions": suggestions,
            "interaction_id": interaction_id,
            "form_data_update": {
                "ai_suggested_followups": suggestions,
            },
        }
    except Exception as e:
        return {"success": False, "message": f"Error generating suggestions: {str(e)}", "suggestions": suggestions}
    finally:
        db.close()


@tool
def summarize_interaction(
    interaction_id: int,
    hcp_name: str,
    topics_discussed: str,
    sentiment: str,
    materials_shared: Optional[list] = None,
    samples_distributed: Optional[list] = None,
    outcomes: Optional[str] = None,
) -> dict:
    """
    Generate a concise professional summary of the HCP interaction.
    Use this to condense verbose interaction notes into a clean, structured summary
    that can be used for reporting or sharing with managers.
    Updates the outcomes field with the summary.
    """
    materials_str = ", ".join(materials_shared) if materials_shared else "none"
    samples_str = ", ".join(samples_distributed) if samples_distributed else "none"

    summary_lines = [
        f"Interaction Summary with {hcp_name}:",
        f"• Topics covered: {topics_discussed}",
        f"• HCP Sentiment: {sentiment}",
    ]

    if materials_shared:
        summary_lines.append(f"• Materials shared: {materials_str}")
    if samples_distributed:
        summary_lines.append(f"• Samples distributed: {samples_str}")
    if outcomes:
        summary_lines.append(f"• Key outcomes: {outcomes}")

    summary = "\n".join(summary_lines)

    db = _get_db()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if interaction and not interaction.outcomes:
            interaction.outcomes = summary
            db.commit()
            db.refresh(interaction)

        return {
            "success": True,
            "message": "Interaction summary generated successfully.",
            "summary": summary,
            "interaction_id": interaction_id,
        }
    except Exception as e:
        return {"success": False, "message": f"Error summarizing: {str(e)}", "summary": summary}
    finally:
        db.close()