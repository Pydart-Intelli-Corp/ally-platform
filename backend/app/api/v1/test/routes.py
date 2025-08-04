"""
Test endpoints for development and debugging
"""

from fastapi import APIRouter
from pydantic import BaseModel
import redis
import mysql.connector
from sqlalchemy import create_engine, text
import google.generativeai as genai
import weaviate
from datetime import datetime

from app.core.config import config, get_company_name, is_feature_enabled, get_ai_model

router = APIRouter()


# Pydantic models for testing
class TestResponse(BaseModel):
    message: str
    timestamp: str
    dependencies_status: dict


class UserInput(BaseModel):
    text: str


@router.get("/dependencies", response_model=TestResponse)
async def test_dependencies():
    """Test all installed backend dependencies"""
    status = {
        "fastapi": "✅ Working",
        "pydantic": "✅ Working",
        "uvicorn": "✅ Working",
    }

    # Test Redis connection (will fail if Redis not running, but library works)
    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        status["redis"] = "✅ Connected"
    except Exception as e:
        status["redis"] = f"⚠️ Library works, server not running: {str(e)[:50]}"

    # Test SQLAlchemy (in-memory SQLite for testing)
    try:
        engine = create_engine("sqlite:///:memory:")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone()[0] == 1:
                status["sqlalchemy"] = "✅ Working"
    except Exception as e:
        status["sqlalchemy"] = f"❌ Error: {str(e)[:50]}"

    # Test MySQL Connector (library import only)
    try:
        import mysql.connector

        status["mysql_connector"] = "✅ Library imported"
    except Exception as e:
        status["mysql_connector"] = f"❌ Import error: {str(e)[:50]}"

    # Test Google Generative AI (library import only)
    try:
        import google.generativeai as genai

        status["google_generativeai"] = "✅ Library imported"
    except Exception as e:
        status["google_generativeai"] = f"❌ Import error: {str(e)[:50]}"

    # Test Weaviate Client (library import only)
    try:
        import weaviate

        status["weaviate_client"] = "✅ Library imported"
    except Exception as e:
        status["weaviate_client"] = f"❌ Import error: {str(e)[:50]}"

    return TestResponse(
        message="Backend dependencies test completed",
        timestamp=datetime.now().isoformat(),
        dependencies_status=status,
    )


@router.post("/pydantic")
async def test_pydantic_validation(user_input: UserInput):
    """Test Pydantic model validation"""
    return {
        "received_text": user_input.text,
        "text_length": len(user_input.text),
        "message": "✅ Pydantic validation working!",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/config-loader")
async def test_config_loader():
    """Test the configuration loader functionality"""
    try:
        # Test direct config access
        company_name = config["branding"]["companyName"]

        # Test convenience functions
        primary_color = config["branding"]["primaryColor"]
        ai_model = get_ai_model()
        chat_enabled = is_feature_enabled("chatEnabled")

        # Test multiple configuration values
        config_info = {
            "company_name": company_name,
            "primary_color": primary_color,
            "ai_model": ai_model,
            "features": {
                "chat_enabled": chat_enabled,
                "voice_enabled": is_feature_enabled("voiceEnabled"),
                "analytics_enabled": is_feature_enabled("analyticsEnabled"),
            },
            "ui_settings": {
                "layout": config["ui"]["layout"],
                "dark_mode": config["ui"]["darkMode"],
                "theme_toggle": config["ui"]["themeToggle"],
            },
            "ai_settings": {
                "temperature": config["ai"]["temperature"],
                "max_tokens": config["ai"]["maxTokens"],
                "response_format": config["ai"]["responseFormat"],
            },
        }

        return {
            "message": "✅ Configuration loader working!",
            "timestamp": datetime.now().isoformat(),
            "config_loaded": True,
            "configuration": config_info,
            "meta": {
                "client_id": config["meta"]["clientId"],
                "version": config["meta"]["version"],
                "last_updated": config["meta"]["lastUpdated"],
            },
        }

    except Exception as e:
        return {
            "message": f"❌ Configuration loader error: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "config_loaded": False,
            "error": str(e),
        }
