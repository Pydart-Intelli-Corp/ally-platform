#!/usr/bin/env python3
"""
Configuration Schema Validation Script
Tests and validates the client configuration schema using jsonschema.
"""

import json
import os
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator
from datetime import datetime


def load_json_file(file_path: str):
    """Load and parse a JSON file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        return None


def validate_schema_structure(schema):
    """Validate that the schema itself is valid"""
    try:
        Draft7Validator.check_schema(schema)
        print("✅ Schema structure is valid")
        return True
    except Exception as e:
        print(f"❌ Schema structure is invalid: {e}")
        return False


def validate_config_against_schema(config, schema):
    """Validate a configuration against the schema"""
    try:
        validate(instance=config, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def test_schema_validation():
    """Test the configuration schema with various test cases"""
    print("🧪 Testing Configuration Schema Validation")
    print("=" * 50)

    # Get paths
    config_dir = Path(__file__).parent
    schema_path = config_dir / "client-config.schema.json"
    default_config_path = config_dir / "default-config.json"

    # Load schema
    schema = load_json_file(schema_path)
    if not schema:
        return False

    # Validate schema structure
    if not validate_schema_structure(schema):
        return False

    # Load default configuration
    default_config = load_json_file(default_config_path)
    if not default_config:
        return False

    print(f"\n📋 Testing Default Configuration")
    print("-" * 30)

    # Test default configuration
    is_valid, error = validate_config_against_schema(default_config, schema)
    if is_valid:
        print("✅ Default configuration is valid")
    else:
        print(f"❌ Default configuration is invalid: {error}")
        return False

    # Test cases
    test_cases = [
        {
            "name": "Minimal Valid Configuration",
            "config": {
                "meta": {
                    "version": "1.0.0",
                    "clientId": "test-client",
                    "lastUpdated": datetime.now().isoformat(),
                },
                "branding": {"companyName": "Test Company", "primaryColor": "#FF0000"},
                "features": {
                    "chatEnabled": True,
                    "voiceEnabled": False,
                    "fileUploadEnabled": True,
                    "realTimeEnabled": True,
                    "analyticsEnabled": True,
                    "notificationsEnabled": True,
                    "collaborationEnabled": False,
                    "apiAccessEnabled": False,
                    "exportEnabled": True,
                },
                "ui": {
                    "layout": "modern",
                    "darkMode": True,
                    "themeToggle": True,
                    "sidebarCollapsible": True,
                    "compactMode": False,
                    "animationsEnabled": True,
                    "accessibilityMode": False,
                },
                "ai": {
                    "model": "gemini-2.5-flash-lite",
                    "temperature": 0.7,
                    "maxTokens": 2000,
                    "responseFormat": "markdown",
                },
            },
            "should_be_valid": True,
        },
        {
            "name": "Invalid Client ID (too short)",
            "config": {
                "meta": {
                    "version": "1.0.0",
                    "clientId": "ab",  # Too short
                    "lastUpdated": datetime.now().isoformat(),
                },
                "branding": {"companyName": "Test Company", "primaryColor": "#FF0000"},
                "features": {},
                "ui": {},
                "ai": {"model": "gemini-2.5-flash-lite"},
            },
            "should_be_valid": False,
        },
        {
            "name": "Invalid Primary Color Format",
            "config": {
                "meta": {
                    "version": "1.0.0",
                    "clientId": "test-client",
                    "lastUpdated": datetime.now().isoformat(),
                },
                "branding": {
                    "companyName": "Test Company",
                    "primaryColor": "red",  # Invalid format
                },
                "features": {},
                "ui": {},
                "ai": {"model": "gemini-2.5-flash-lite"},
            },
            "should_be_valid": False,
        },
        {
            "name": "Invalid AI Model",
            "config": {
                "meta": {
                    "version": "1.0.0",
                    "clientId": "test-client",
                    "lastUpdated": datetime.now().isoformat(),
                },
                "branding": {"companyName": "Test Company", "primaryColor": "#FF0000"},
                "features": {},
                "ui": {},
                "ai": {"model": "invalid-model"},  # Not in enum
            },
            "should_be_valid": False,
        },
        {
            "name": "Valid with All Optional Fields",
            "config": {
                "meta": {
                    "version": "1.0.0",
                    "clientId": "full-test-client",
                    "lastUpdated": datetime.now().isoformat(),
                    "configName": "Full Test Configuration",
                    "description": "A comprehensive test configuration with all fields",
                },
                "branding": {
                    "companyName": "Full Test Company",
                    "logoUrl": "https://example.com/logo.png",
                    "faviconUrl": "https://example.com/favicon.ico",
                    "primaryColor": "#3B82F6",
                    "secondaryColor": "#64748B",
                    "accentColor": "#EF4444",
                    "font": "roboto",
                    "customCss": "body { background-color: #f0f0f0; }",
                },
                "features": {
                    "chatEnabled": True,
                    "voiceEnabled": True,
                    "fileUploadEnabled": True,
                    "realTimeEnabled": True,
                    "analyticsEnabled": True,
                    "notificationsEnabled": True,
                    "collaborationEnabled": True,
                    "apiAccessEnabled": True,
                    "exportEnabled": True,
                },
                "ui": {
                    "layout": "dashboard",
                    "darkMode": False,
                    "themeToggle": True,
                    "sidebarCollapsible": True,
                    "compactMode": True,
                    "animationsEnabled": True,
                    "accessibilityMode": True,
                },
                "ai": {
                    "model": "gpt-4o",
                    "promptTemplate": "You are a helpful assistant for {companyName}.",
                    "temperature": 0.5,
                    "maxTokens": 4000,
                    "systemMessage": "Be helpful and professional.",
                    "responseFormat": "json",
                },
                "languages": {
                    "default": "en",
                    "supported": ["en", "es", "fr"],
                    "rtlSupport": False,
                    "autoDetect": True,
                },
                "analytics": {
                    "enabled": True,
                    "trackingId": "GA-123456789",
                    "customEvents": True,
                    "userJourneyTracking": True,
                    "performanceMonitoring": True,
                    "errorTracking": True,
                },
            },
            "should_be_valid": True,
        },
    ]

    print(f"\n🧪 Running Test Cases")
    print("-" * 30)

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")

        is_valid, error = validate_config_against_schema(test_case["config"], schema)
        expected = test_case["should_be_valid"]

        if is_valid == expected:
            if is_valid:
                print(f"✅ PASS - Configuration is valid as expected")
            else:
                print(f"✅ PASS - Configuration is invalid as expected")
                print(f"   Error: {error}")
        else:
            all_passed = False
            if is_valid and not expected:
                print(f"❌ FAIL - Expected invalid but got valid")
            else:
                print(f"❌ FAIL - Expected valid but got invalid")
                print(f"   Error: {error}")

    print(f"\n📊 Test Results")
    print("=" * 30)

    if all_passed:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


def main():
    """Main function"""
    print("🔧 Ally Platform Configuration Schema Validator")
    print("=" * 60)

    success = test_schema_validation()

    if success:
        print("\n🎉 Schema validation completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Schema validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
