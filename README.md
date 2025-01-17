# PwC-Challenge: Financial Management System
#### Note:
- For security reasons, the .env file is not published in this public repository. If needed, please contact me and I'll send it to you.
- Solution Hosted in Render: [Link Text](https://pwc-challenge.onrender.com)
  
## Overview

This Financial Management System is a robust, role-based API designed to streamline financial operations for businesses. Built with FastAPI and SQLAlchemy, the system provides comprehensive features for managing clients, financial transactions, and invoices with strong security and access control.

## Key Features

- 🔒 Role-Based Access Control
- 👥 User and Client Management
- 💰 Financial Transaction Tracking
- 📄 Invoice Management
- 🔍 Advanced Search and Filtering
- 📊 Financial Reporting

## Technology Stack

- **Backend**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Testing**: Pytest
- **PDF Generation**: ReportLab
- **Database Migration**: Alembic

## Development Approach

### Architecture
The project follows a layered, clean architecture:
- **Models**: SQLAlchemy database models
- **Repositories**: Data access layer
- **Services**: Business logic implementation
- **Controllers**: Request handling and validation
- **Routes**: API endpoint definitions

### Security Considerations
- Bcrypt password hashing
- JWT-based authentication
- Role-based permissions
- Input validation at multiple levels

### Testing Strategy
Comprehensive test suite covering:
- Unit testing
- Integration testing
- Model validations
- Schema validations
- API endpoint behaviors
- Authorization checks
- Business logic scenarios

## Getting Started

## User Types and Workflow

### User Roles and Permissions

The Financial Management System is designed to serve different types of users with carefully defined access levels:

#### 1. Admin Users
- **Full System Access**
- Can perform all actions across the platform
- Responsibilities:
  - Create and manage client profiles
  - Add and manage user accounts
  - Perform system-wide configurations
  - Delete client records
  - Generate comprehensive reports

#### 2. Finance Team Users
- **Transactional and Financial Management**
- Core financial operations specialists
- Permissions:
  - Create, view, update, and delete financial transactions
  - Generate and manage invoices
  - Process payments
  - Conduct financial reporting
  - Search and filter financial data

#### 3. Auditor Users
- **Compliance and Oversight**
- Read-only access for financial monitoring
- Capabilities:
  - View all financial transactions
  - Review invoices
  - Generate financial reports
  - Verify financial records
  - Cannot modify or delete records

#### 4. Client Users
- **Self-Service and Limited Access**
- View and manage their own financial information
- Permissions:
  - View their own transactions
  - Access their invoices
  - Generate personal financial reports
  - Cannot modify system-wide data

### Typical Workflow Scenarios

#### Scenario 1: New Client Onboarding
1. Admin creates a new client profile
2. System automatically generates a client user account
3. Client receives login credentials
4. Client can now view their financial information

#### Scenario 2: Financial Transaction Processing
1. Finance user logs a new transaction for a client
2. Transaction is recorded with timestamp and details
3. System automatically updates client financial records
4. Auditors can review the transaction
5. Client can view the transaction in their history

#### Scenario 3: Invoice Management
1. Finance user generates an invoice for a client
2. Invoice is created with due date and amount
3. System tracks payment status (Pending, Partially Paid, Paid)
4. Automatic status updates based on payment received
5. Client notified of invoice details
6. Overdue invoices flagged for follow-up

#### Scenario 4: Financial Reporting
1. Admin or Finance user generates a financial report
2. Report includes:
   - Transaction history
   - Invoice details
   - Payment status
   - Comprehensive financial overview
3. Report can be downloaded as PDF
4. Auditors can review report for compliance

### Resource-Level Permissions

The system defines granular actions for each primary resource:

| Resource             | Admin         | Finance       | Auditor       | Client        |
|---------------------|---------------|---------------|---------------|---------------|
| Clients             | CRUD          | CRU           | Read          | Read (Own)    |
| Users               | CRUD          | -             | -             | -             |
| Financial Transactions | CRUD      | CRUD          | Read          | Read (Own)    |
| Audit Logs          | CRUD          | -             | Read          | -             |
| Invoices            | CRUD          | CRUD          | Read          | Read (Own)    |

**Notation Legend:**
- **CRUD**: Create, Read, Update, Delete
- **CRU**: Create, Read, Update
- **Read**: View-only access
- **Read (Own)**: Access limited to user's own records
- **-**: No access

## Development Steps

The project was developed following a systematic, layer-by-layer approach:

1. **Database Setup**
   - Create database tables
   - Populate roles and permissions

2. **Models and Schemas**
   - Implement FastAPI models
   - Create Pydantic schemas
   - Write comprehensive pytest tests for models and schemas

3. **Authentication System**
   - Implement basic routes
   - Develop login functionality
   - Create authentication utilities
   - Build authentication layers:
     - Route
     - Controller
     - Service
     - Repository
   - Write authentication tests

4. **Client SignUp**
   - Add signup functionality
   - Implement user registration tests

5. **Client Management**
   - Create client routes
   - Develop client CRUD operations
   - Implement client-related tests

6. **Financial Transactions**
   - Develop financial transaction routes
   - Implement transaction management
   - Write comprehensive transaction tests

7. **Invoice Management**
   - Create invoice routes
   - Implement invoice lifecycle management
   - Develop invoice-related tests

8. **Reporting**
   - Add report generation endpoint
   - Implement PDF report utility
   - Create reporting tests

Swagger UI is available at `/docs` for interactive API exploration.
