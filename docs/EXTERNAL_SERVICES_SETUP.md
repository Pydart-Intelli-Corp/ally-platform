# External Services Configuration Guide

## Overview

This document explains how to configure the Ally Platform with external services including MySQL database, Weaviate vector database, Google AI API, and SMTP email services.

## 🔧 Configuration Files Updated

### Environment Files

- `.env.development` - Updated with external service credentials for development
- `.env.production` - New production environment configuration
- `config/production-config.json` - Production-specific feature configuration

### Service Credentials Configured

#### 1. MySQL Database (RDP-Main-Server)

```env
DATABASE_URL=mysql://root:123@456@RDP-Main-Server:3306/psrapp
MYSQL_HOST=RDP-Main-Server
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123@456
MYSQL_DATABASE=psrapp
```

#### 2. Weaviate Vector Database

```env
WEAVIATE_URL=https://chmjnz2nq6wviibztt7chg.c0.asia-southeast1.gcp.weaviate.cloud
WEAVIATE_API_KEY=QTRpTHdkcytOWWFqVW9CeV91UmZmMlNlcytFZUxlcVA5aFo4WjBPRHFOdlNtOU9qaDFxOG12eTJSYW9nPV92MjAw
```

#### 3. Google AI API (Gemini)

```env
GOOGLE_AI_API_KEY=AIzaSyB1Cr_w2ioWBlDgSWlkMjYRFPzxAq_AkLc
GEMINI_MODEL=gemini-2.5-flash-lite
```

#### 4. SMTP Email Service (Gmail)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=info.pydart@gmail.com
SMTP_PASSWORD=rjif lojs pzbq bdcz
SMTP_USE_TLS=true
```

## 🚀 Getting Started

### 1. Test Service Connections

Run the service connection tests to verify all credentials work:

```bash
# From the project root
cd scripts
python test_services.py
```

This will test:

- ✅ MySQL database connection
- ✅ Weaviate vector database
- ✅ Google AI API
- ✅ SMTP email service

### 2. Database Setup

The application will automatically create the required tables when it starts. To ensure the database is properly configured:

```bash
# Run database migration (if needed)
cd config
python migrate_database.py
```

### 3. Configuration Validation

Validate your configuration files:

```bash
cd config
python validate_schema.py
```

## 🏗️ Architecture Changes

### Database Configuration

- **Previous**: Local MySQL in Docker container
- **Current**: External MySQL server (RDP-Main-Server)
- **Impact**: Better performance and persistence for production

### AI Integration

- **Model**: Gemini 2.5 Flash Lite
- **API**: Google AI Generative Language API
- **Features**: Real-time chat, content generation, smart responses

### Vector Database

- **Service**: Weaviate Cloud
- **Usage**: Semantic search, document embeddings, RAG capabilities
- **Region**: Asia-Southeast1 (optimal for your location)

### Email Service

- **Provider**: Gmail SMTP
- **From Address**: info.pydart@gmail.com
- **Features**: Welcome emails, password resets, notifications

## 🔒 Security Considerations

### Production Deployment

1. **Environment Variables**: Use `.env.production` for production deployments
2. **API Keys**: Ensure all API keys are properly secured
3. **Database Access**: Verify database firewall rules allow application access
4. **SMTP Security**: Using app-specific password for Gmail

### Configuration Management

- Client configurations are stored in the MySQL database
- Redis caching for improved performance
- JSON Schema validation for all configuration updates
- Audit logging for configuration changes

## 📋 Next Steps

### Phase 3: User Authentication

With the database and configuration system ready, you can now implement:

1. User registration and login
2. JWT token management
3. Role-based access control
4. Client-specific user management

### AI Features Integration

1. Chat interface with Gemini AI
2. Document upload and processing with Weaviate
3. Semantic search capabilities
4. Context-aware responses

### Email Notifications

1. Welcome email templates
2. Password reset workflows
3. System notifications
4. User engagement emails

## 🛠️ Troubleshooting

### Database Connection Issues

1. Verify RDP-Main-Server is accessible from your application server
2. Check MySQL service is running on port 3306
3. Confirm user 'root' has access to 'psrapp' database
4. Test connection with: `python scripts/test_services.py`

### API Key Issues

1. Google AI API: Verify key is active and has Generative Language API enabled
2. Weaviate: Ensure cluster is running and key has proper permissions
3. Check API quotas and usage limits

### SMTP Issues

1. Gmail: Verify app-specific password is correct
2. Check if 2FA is enabled and app password is generated
3. Test connection with: `python scripts/test_services.py`

## 📞 Support

For configuration issues or questions:

1. Run the test scripts first: `python scripts/test_services.py`
2. Check application logs for detailed error messages
3. Verify all environment variables are loaded correctly
