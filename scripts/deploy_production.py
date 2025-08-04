#!/usr/bin/env python3
"""
Production Deployment Script for Ally Platform
Sets up the platform with external services and production configuration.
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionDeployer:
    """Handle production deployment with external services"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / ".env.production"

    def check_prerequisites(self) -> bool:
        """Check if all required files and services are ready"""
        logger.info("🔍 Checking prerequisites...")

        required_files = [
            ".env.production",
            "config/production-config.json",
            "config/client-config.schema.json",
            "backend/app/main.py",
            "backend/app/config_manager.py",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            logger.error(f"❌ Missing required files: {missing_files}")
            return False

        logger.info("✅ All required files found")
        return True

    def test_external_services(self) -> bool:
        """Test all external service connections"""
        logger.info("🧪 Testing external services...")

        try:
            # Run the service test script
            test_script = self.project_root / "scripts" / "test_services.py"
            result = subprocess.run(
                [sys.executable, str(test_script)], capture_output=True, text=True
            )

            if result.returncode == 0:
                logger.info("✅ All external services are working")
                return True
            else:
                logger.error("❌ Some external services failed")
                logger.error(result.stderr)
                return False

        except Exception as e:
            logger.error(f"❌ Failed to test services: {str(e)}")
            return False

    def setup_database(self) -> bool:
        """Initialize database tables and configuration"""
        logger.info("🗄️ Setting up database...")

        try:
            # Load production environment
            self.load_env_file()

            # Run database migration
            migration_script = self.project_root / "config" / "migrate_database.py"
            if migration_script.exists():
                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info("✅ Database setup completed")
                    return True
                else:
                    logger.error(f"❌ Database setup failed: {result.stderr}")
                    return False
            else:
                logger.warning("⚠️ Migration script not found, skipping database setup")
                return True

        except Exception as e:
            logger.error(f"❌ Database setup failed: {str(e)}")
            return False

    def load_env_file(self):
        """Load production environment variables"""
        logger.info("🔧 Loading production environment...")

        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            os.environ[key] = value

            logger.info("✅ Production environment loaded")
        else:
            logger.error("❌ Production environment file not found")
            raise FileNotFoundError(f"Environment file not found: {self.env_file}")

    def start_backend(self) -> bool:
        """Start the FastAPI backend server"""
        logger.info("🚀 Starting backend server...")

        try:
            # Change to backend directory
            backend_dir = self.project_root / "backend"

            # Start uvicorn server
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--env-file",
                str(self.env_file),
            ]

            logger.info(f"Starting server with command: {' '.join(cmd)}")
            logger.info("Backend server starting on http://0.0.0.0:8000")
            logger.info("API documentation available at: http://0.0.0.0:8000/docs")
            logger.info("Configuration API: http://0.0.0.0:8000/api/v1/config/")

            # Start the server (this will block)
            subprocess.run(cmd, cwd=backend_dir)

            return True

        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {str(e)}")
            return False

    def deploy(self):
        """Run the complete deployment process"""
        logger.info("🚀 Starting Ally Platform production deployment...")
        print("=" * 60)

        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites check failed")
            sys.exit(1)

        # Step 2: Test external services
        if not self.test_external_services():
            logger.error("❌ External services test failed")
            sys.exit(1)

        # Step 3: Setup database
        if not self.setup_database():
            logger.error("❌ Database setup failed")
            sys.exit(1)

        print("=" * 60)
        logger.info("🎉 Production deployment preparation completed!")
        logger.info("📋 Deployment Summary:")
        logger.info("  ✅ Prerequisites verified")
        logger.info("  ✅ External services tested")
        logger.info("  ✅ Database initialized")
        logger.info("  🚀 Ready to start backend server")

        print("=" * 60)

        # Step 4: Start backend server
        self.start_backend()


if __name__ == "__main__":
    deployer = ProductionDeployer()
    deployer.deploy()
