# PwC-Challenge: Financial Management System

## Overview

A robust Financial Management System built with FastAPI, implementing clean architecture and modern design principles. The system provides comprehensive features for managing clients, financial transactions, and invoices with strong security and role-based access control.

## Key Features

- 🔒 Role-Based Access Control
- 👥 User and Client Management
- 💰 Financial Transaction Tracking
- 📄 Invoice Management
- 🔍 Advanced Search and Filtering
- 📊 Financial Report Generation

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Testing**: Pytest
- **Documentation**: OpenAPI/Swagger
- **Deployment**: Render

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

| Resource               | Admin | Finance | Auditor | Client     |
| ---------------------- | ----- | ------- | ------- | ---------- |
| Clients                | CRUD  | CRU     | Read    | Read (Own) |
| Users                  | CRUD  | -       | -       | -          |
| Financial Transactions | CRUD  | CRUD    | Read    | Read (Own) |
| Audit Logs             | CRUD  | -       | Read    | -          |
| Invoices               | CRUD  | CRUD    | Read    | Read (Own) |

**Notation Legend:**

- **CRUD**: Create, Read, Update, Delete
- **CRU**: Create, Read, Update
- **Read**: View-only access
- **Read (Own)**: Access limited to user's own records
- **-**: No access

## Clean Architecture

The system implements a layered architecture following SOLID principles, with clear separation of concerns:

### 1. Domain Layer

- **Entities**: Core business objects and logic
  ```
  /entities
    - client.py
    - invoice.py
    - financial_transaction.py
    - user.py
    - audit_log.py
    - permission.py
  ```
- Contains business rules and validations
- Framework-independent

### 2. Application Layer

- **Interfaces**: Abstract contracts for services and repositories
  ```
  /interfaces
    /services
    /repositories
  ```
- **DTOs**: Data transfer objects for inter-layer communication
  ```
  /schemas/dto
  ```

### 3. Infrastructure Layer

- **Models**: Database models using SQLAlchemy

  ```
  /models

  ```

- **Repository Implementations**: Data access logic
  ```
  /repositories
  ```

### 4. Presentation Layer

- **Request/Response Models**: Pydantic schemas for validation
  ```
  /schemas
    /request
    /response
  ```
- **Controllers**: Request handling and business logic coordination
- **Routes**: API endpoint definitions

## Dependency Management

### Inversion of Control (IoC)

The system implements IoC through interfaces and dependency injection:

```python
# Interface definition
class IClientService(ABC):
    @abstractmethod
    async def create_client(self, client_dto: ClientDTO) -> ClientDTO:
        pass

# Service implementation
class ClientService(IClientService):
    def __init__(self, client_repository: IClientRepository):
        self.client_repository = client_repository
```

### Dependency Injection Container

Centralized dependency management using `dependency-injector`

## Data Flow & Request Lifecycle

1. **HTTP Request → Route**

2. **Route → Controller**

3. **Controller → Service**

4. **Service → Repository**

## Benefits of This Architecture

1. **Maintainability**

   - Clear separation of concerns
   - Isolated business logic
   - Framework independence

2. **Testability**

   - Easily mockable dependencies
   - Isolated component testing
   - Clear boundaries

3. **Flexibility**

   - Swappable implementations
   - Database agnostic
   - Framework independent core

4. **Security**
   - Centralized authentication
   - Role-based access control
   - Input validation at multiple levels

### Security Considerations

- Bcrypt password hashing
- JWT-based authentication
- Role-based permissions
- Input validation at multiple levels

## Getting Started

1. Clone the repository
2. Create a `.env` file based on `.env.example`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start the server: `uvicorn app.main:app --reload`

## API Documentation

- Interactive API documentation: `/docs`
- ReDoc alternative: `/redoc`
- Hosted version: https://pwc-challenge.onrender.com/docs

## Testing

Run tests with: `pytest`

## Notes

- For security reasons, the `.env` file is not published
- Sample data and accounts available in 'sample_data' folder
