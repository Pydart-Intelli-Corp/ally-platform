#!/usr/bin/env python3
"""
Test Database and Service Connections
Tests all the external services with the provided credentials.
"""

import os
import sys
import mysql.connector
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServiceTester:
    """Test all external service connections"""

    def __init__(self):
        # Load environment variables
        self.mysql_config = {
            "host": "RDP-Main-Server",
            "port": 3306,
            "user": "root",
            "password": "123@456",
            "database": "psrapp",
        }

        self.weaviate_config = {
            "url": "https://chmjnz2nq6wviibztt7chg.c0.asia-southeast1.gcp.weaviate.cloud",
            "api_key": "QTRpTHdkcytOWWFqVW9CeV91UmZmMlNlcytFZUxlcVA5aFo4WjBPRHFOdlNtOU9qaDFxOG12eTJSYW9nPV92MjAw",
        }

        self.google_api_key = "AIzaSyB1Cr_w2ioWBlDgSWlkMjYRFPzxAq_AkLc"

        self.smtp_config = {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": "info.pydart@gmail.com",
            "password": "rjif lojs pzbq bdcz",
        }

    def test_mysql_connection(self) -> bool:
        """Test MySQL database connection"""
        logger.info("Testing MySQL connection...")
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                logger.info(f"✅ MySQL connection successful! Version: {version[0]}")

                # Test database access
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"📊 Found {len(tables)} tables in database 'psrapp'")

                cursor.close()
                connection.close()
                return True
        except Exception as e:
            logger.error(f"❌ MySQL connection failed: {str(e)}")
            return False

    def test_weaviate_connection(self) -> bool:
        """Test Weaviate vector database connection"""
        logger.info("Testing Weaviate connection...")
        try:
            headers = {
                "Authorization": f'Bearer {self.weaviate_config["api_key"]}',
                "Content-Type": "application/json",
            }

            # Test basic connectivity
            response = requests.get(
                f'{self.weaviate_config["url"]}/v1/meta', headers=headers, timeout=10
            )

            if response.status_code == 200:
                meta_info = response.json()
                logger.info(f"✅ Weaviate connection successful!")
                logger.info(f"🔗 Version: {meta_info.get('version', 'Unknown')}")
                return True
            else:
                logger.error(
                    f"❌ Weaviate connection failed: HTTP {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Weaviate connection failed: {str(e)}")
            return False

    def test_google_ai_api(self) -> bool:
        """Test Google AI API connection"""
        logger.info("Testing Google AI API...")
        try:
            # Test with a simple request to Gemini API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={self.google_api_key}"

            payload = {"contents": [{"parts": [{"text": "Say hello in one word"}]}]}

            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Google AI API connection successful!")
                logger.info(f"🤖 Test response received from Gemini")
                return True
            else:
                logger.error(f"❌ Google AI API failed: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Google AI API connection failed: {str(e)}")
            return False

    def test_smtp_connection(self) -> bool:
        """Test SMTP email connection"""
        logger.info("Testing SMTP connection...")
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"])
            server.starttls()  # Enable encryption
            server.login(self.smtp_config["username"], self.smtp_config["password"])

            logger.info("✅ SMTP connection and authentication successful!")

            # Optionally send a test email (commented out to avoid spam)
            # self._send_test_email(server)

            server.quit()
            return True

        except Exception as e:
            logger.error(f"❌ SMTP connection failed: {str(e)}")
            return False

    def _send_test_email(self, server):
        """Send a test email (optional)"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["username"]
            msg["To"] = self.smtp_config["username"]  # Send to self
            msg["Subject"] = "Ally Platform - SMTP Test"

            body = "This is a test email from Ally Platform configuration setup."
            msg.attach(MIMEText(body, "plain"))

            server.send_message(msg)
            logger.info("📧 Test email sent successfully!")

        except Exception as e:
            logger.error(f"❌ Test email failed: {str(e)}")

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all service connection tests"""
        logger.info("🚀 Starting service connection tests...")
        print("=" * 60)

        results = {
            "mysql": self.test_mysql_connection(),
            "weaviate": self.test_weaviate_connection(),
            "google_ai": self.test_google_ai_api(),
            "smtp": self.test_smtp_connection(),
        }

        print("=" * 60)
        logger.info("📊 Test Results Summary:")

        for service, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"  {service.upper()}: {status}")

        success_count = sum(results.values())
        total_count = len(results)

        if success_count == total_count:
            logger.info(f"🎉 All {total_count} services are working correctly!")
        else:
            logger.warning(f"⚠️  {success_count}/{total_count} services are working.")

        return results


if __name__ == "__main__":
    tester = ServiceTester()
    results = tester.run_all_tests()

    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)
    else:
        sys.exit(0)
