# Ally Platform

A comprehensive SaaS platform with white-label configuration management built with modern technologies including Next.js, FastAPI, MySQL, and Redis, fully containerized with Docker.

## 🎯 Project Status

**✅ SYSTEM FULLY OPERATIONAL - VERIFIED JANUARY 4, 2025**

### ✅ PHASE 1: PROJECT INITIALIZATION - COMPLETED

- Environment setup with all required tools
- Complete project structure with frontend/backend
- All dependencies installed and tested
- Production-ready Docker containerization

### ✅ PHASE 2: CORE DEVELOPMENT - COMPLETED

- **Configuration Management System**: Full API with environment-specific configs
- **Frontend Application**: Next.js with React components and configuration system
- **Backend API**: FastAPI with health checks, configuration endpoints, and database integration
- **Docker Services**: Multi-container architecture with MySQL, Redis, backend, and frontend
- **Clean Codebase**: Removed 25+ redundant files, organized structure, ready for production

### ✅ PHASE 3: DATABASE SCHEMA & MODELS - COMPLETED

- **Multi-Tenant Database Architecture**: 8 comprehensive models with tenant isolation
- **Production Azure MySQL Deployment**: SSL-secured cloud database with .NET connection string support
- **SQLAlchemy 2.0 Integration**: Modern async ORM with full relationship mapping
- **Alembic Migration System**: Automated schema management and version control
- **Service Layer Implementation**: Complete CRUD operations for all database models
- **Azure Production Environment**: Production-ready deployment on Azure MySQL

### 🚀 SYSTEM STATUS

- **All Services Running**: Frontend (3000), Backend (8001), MySQL (3307), Redis (6379), phpMyAdmin (8080)
- **Production Database**: Azure MySQL with SSL encryption and 8 tables deployed
- **API Endpoints Verified**: Health checks, configuration management, branding, feature flags
- **Frontend Pages Working**: Main app, API test page, configuration interface
- **Database & Cache**: MySQL and Redis connections verified, Alembic migrations applied
- **Documentation**: API docs available at http://localhost:8001/docs

## 🏗️ Architecture

```
ally-platform/
├── frontend/          # Next.js 15 with TypeScript & TailwindCSS
├── backend/           # FastAPI with Python 3.11 & SQLAlchemy 2.0
│   ├── app/models/    # 8 comprehensive database models
│   ├── app/services/  # Complete service layer with async CRUD
│   ├── app/core/      # Database & environment configuration
│   └── alembic/       # Database migration system
├── docker/            # Docker configurations & MySQL init scripts
├── docs/              # Comprehensive documentation (Phases 1-3)
├── scripts/           # Build and deployment scripts
├── tests/             # Test files
├── config/            # Configuration files
└── .vscode/           # VS Code workspace settings
```

## 🛠️ Technology Stack

### Frontend

- **Next.js 15.4.5** - React framework with TypeScript
- **TailwindCSS 4** - Utility-first CSS framework
- **Material-UI** - React component library
- **Zustand** - State management
- **Framer Motion** - Animation library
- **React Hook Form** - Form handling
- **Axios** - HTTP client

### Backend

- **FastAPI 0.116.1** - Modern Python web framework
- **SQLAlchemy 2.0.42** - Modern async Database ORM with comprehensive models
- **Alembic 1.13.0** - Database migration management
- **Pydantic 2.11.7** - Data validation
- **Uvicorn 0.35.0** - ASGI server
- **MySQL Connector & PyMySQL** - Database drivers with SSL support
- **Redis 5.0.1** - Caching layer
- **Celery 5.3.4** - Task queue
- **Google Generative AI** - AI integration
- **Weaviate Client** - Vector database

### Infrastructure

- **Docker & Docker Compose** - Containerization
- **MySQL 8.0** - Primary database (local) + Azure MySQL (production)
- **Redis 7-alpine** - Cache & session store
- **PHPMyAdmin** - Database management interface
- **Azure MySQL** - Production cloud database with SSL/TLS encryption

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** (✅ v21.1.0 installed)
- **Python 3.11+** (✅ v3.11.9 installed)
- **Docker Desktop** (✅ v28.1.1 installed)
- **Git** (✅ v2.45.1 installed)

### 🐳 Docker Setup (Recommended)

1. **Clone and navigate to the project:**

   ```bash
   git clone <repository-url>
   cd ally-platform
   ```

2. **Start all services with Docker Compose:**

   ```bash
   docker-compose up --build -d
   ```

3. **Access the applications:**

   - 🌐 **Frontend App**: http://localhost:3000
   - 🔧 **Backend API Docs**: http://localhost:8000/docs
   - � **API Test Page**: http://localhost:3000/api-test
   - �🗄️ **Database Admin**: http://localhost:8080 (phpMyAdmin)
   - ⚡ **Health Check**: http://localhost:8000/health
   - ⚙️ **Config API**: http://localhost:8000/api/v1/config/

4. **Verify system status:**
   ```bash
   docker-compose ps
   ```

### 🔧 Development Setup

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

#### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# Access at http://localhost:8000
```

## 🐳 Docker Services

| Service        | Port | Description              |
| -------------- | ---- | ------------------------ |
| **Frontend**   | 3000 | Next.js application      |
| **Backend**    | 8000 | FastAPI server with docs |
| **MySQL**      | 3307 | Database server          |
| **Redis**      | 6379 | Cache server             |
| **PHPMyAdmin** | 8080 | Database management      |

### Service Health

All services include health checks and proper dependency management:

- ✅ MySQL health check with 10 retries
- ✅ Redis health check with 5 retries
- ✅ Backend waits for database availability
- ✅ Frontend connects to backend API

## 🧪 Testing & Verification

### API Endpoints

- `GET /` - Health check
- `GET /test-dependencies` - Dependency verification
- `GET /docs` - Interactive API documentation

### Frontend Components

- **TestComponent** - Demonstrates all installed libraries
- **API Test Page** - Backend connectivity testing

### Dependency Testing

Run the backend dependency test:

```bash
python backend/test_dependencies.py
```

## ⚙️ Configuration Management System

The Ally Platform features a comprehensive white-label configuration management system:

### 🔧 Backend API Endpoints

- `GET /api/v1/config/health` - Configuration API health check
- `GET /api/v1/config/` - Get complete configuration
- `GET /api/v1/config/branding` - Get branding configuration
- `GET /api/v1/config/feature/{feature_name}` - Get specific feature flag
- `PUT /api/v1/config/` - Update configuration (with authentication)
- `POST /api/v1/config/validate` - Validate configuration schema

### 🎨 Configuration Features

- **Environment-specific configs**: Development, staging, production
- **Feature flags**: Toggle features dynamically (chat, notifications, dark mode, etc.)
- **White-label branding**: Company name, logo, colors, themes
- **API settings**: Timeout, retry counts, base URLs
- **Real-time updates**: Configuration changes reflect immediately
- **Schema validation**: Ensures configuration integrity
- **Caching layer**: Redis caching for performance

### 🌐 Frontend Integration

- **React Configuration Provider**: Context-based configuration access
- **Environment switching**: Dynamic environment configuration loading
- **Real-time updates**: Live configuration changes without restart
- **TypeScript support**: Full type safety for configuration objects

## 📁 Key Files

```
├── docker-compose.yml           # Multi-service Docker configuration
├── .env.development            # Development environment variables
├── .gitignore                  # Comprehensive exclusions
├── frontend/
│   ├── Dockerfile              # Multi-stage Node.js build
│   ├── package.json            # Frontend dependencies
│   ├── tailwind.config.js      # TailwindCSS configuration
│   └── src/app/components/     # React components
├── backend/
│   ├── Dockerfile              # Python 3.11 container
│   ├── requirements.txt        # Python dependencies
│   ├── app/main.py            # FastAPI application
│   └── test_dependencies.py   # Dependency verification
└── docker/mysql/init/         # Database initialization scripts
```

## 🔧 VS Code Extensions

The following extensions are automatically suggested:

- **Prettier** - Code formatter
- **Docker** - Container management
- **Python** - Python development
- **ESLint** - JavaScript linting
- **Pylint** - Python linting
- **Black Formatter** - Python formatting
- **TailwindCSS IntelliSense** - CSS utilities

## 🌍 Environment Variables

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env.development)

```bash
DATABASE_URL=mysql://ally_user:ally_password@localhost:3307/ally_db
REDIS_URL=redis://localhost:6379
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=ally_user
MYSQL_PASSWORD=ally_password
MYSQL_DATABASE=ally_db
```

### Backend (.env.production)

```bash
ENVIRONMENT=production
DATABASE_URL=Server=psrazuredb.mysql.database.azure.com;Port=3306;UserID=psrcloud;Password=***;Database=ally-db;SslMode=Required;SslCa=DigiCertGlobalRootCA.crt.pem
REDIS_URL=redis://localhost:6379
```

## 🚦 Service Status

Current deployment status:

**Development Environment:**

- ✅ **Frontend**: Next.js app with TypeScript compilation
- ✅ **Backend**: FastAPI with all dependencies working
- ✅ **Database**: MySQL 8.0 with initialization scripts
- ✅ **Cache**: Redis 7-alpine with persistence
- ✅ **Monitoring**: PHPMyAdmin for database management

**Production Environment:**

- ✅ **Azure MySQL**: 8 tables deployed with SSL encryption
- ✅ **Database Models**: Multi-tenant architecture with comprehensive relationships
- ✅ **Migration System**: Alembic with automated schema management
- ✅ **Service Layer**: Complete async CRUD operations
- ✅ **Production Backend**: Running on Azure MySQL with SSL/TLS

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**: If MySQL port 3306 is occupied, we use port 3307
2. **Docker Build Issues**: Use `docker-compose build --no-cache` for clean builds
3. **Health Check Failures**: Allow 40s for MySQL initialization

### Logs

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

## 📈 Next Steps

**Ready for Phase 4 Development:**

- JWT authentication system with Azure AD integration
- RESTful API endpoints for all database operations
- WebSocket support for real-time chat functionality
- Frontend database integration with React hooks
- API rate limiting with tenant-specific quotas
- Production deployment pipeline with Azure Container Apps

## 🤝 Contributing

1. Follow the established project structure
2. Use the configured linting and formatting tools
3. Test changes with Docker Compose
4. Update documentation as needed

---

**🎉 Phases 1-3 Complete!** The platform now has a complete foundation with multi-tenant database architecture deployed on Azure MySQL, ready for authentication and API development.

## Getting Started

```bash
# Navigate to project directory
cd ally-platform

# Check environment
node -v
python --version
docker ps

# Run in development mode
docker-compose up -d

# Run in production mode (Azure MySQL)
cd backend
$env:ENVIRONMENT="production"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 🧹 Recent Updates (January 4, 2025)

### ✅ System Verification Complete

- **All services running**: Frontend, Backend, MySQL, Redis, phpMyAdmin
- **API endpoints tested**: Health checks, configuration management, feature flags
- **Frontend pages verified**: Main app, API test page working correctly
- **Database connections**: MySQL and Redis confirmed operational
- **Documentation**: API docs accessible and complete

### 🗂️ Codebase Cleanup

**Removed 25+ redundant files** for a cleaner, production-ready structure:

- ❌ Removed all `test_*.py` development files
- ❌ Cleaned up duplicate React components
- ❌ Removed build artifacts and cache directories
- ❌ Eliminated unused development demo scripts
- ✅ Preserved all functional code and configurations
- ✅ Maintained clean project structure
- ✅ Optimized for deployment readiness

### 🚀 Current System Architecture

```
✅ Frontend (Next.js 15)     →  http://localhost:3000
✅ Backend (FastAPI)         →  http://localhost:8001
✅ API Documentation        →  http://localhost:8001/docs
✅ Database Admin           →  http://localhost:8080
✅ MySQL Database (Dev)     →  localhost:3307
✅ Azure MySQL (Prod)       →  psrazuredb.mysql.database.azure.com
✅ Redis Cache              →  localhost:6379
```

### 📊 Database Architecture (Phase 3)

**8 Core Models Deployed:**

- **Tenants**: Multi-tenant isolation with subscription management
- **Users**: Role-based access control with tenant associations
- **Configurations**: Dynamic tenant-specific settings storage
- **Chat Sessions**: Real-time chat session management
- **Messages**: AI-powered message storage with threading
- **API Keys**: Secure authentication and access control
- **Audit Logs**: Comprehensive security and compliance logging
- **Client Configurations**: Legacy system migration support

**Production Database:**

- **Azure MySQL**: SSL-encrypted with 25+ performance indexes
- **Migration**: c7b446e62a31 applied successfully
- **Service Layer**: Complete async CRUD operations with SQLAlchemy 2.0

### 📊 Configuration Management

- **5 configuration sections** loaded and validated
- **Environment-specific** settings (dev/staging/prod)
- **Feature flags** system operational
- **White-label branding** system ready
- **Real-time configuration** updates working

## License

TBD
