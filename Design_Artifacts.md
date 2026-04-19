# System Design Artifacts

This document contains the visual design models for the Computer Shop ERP system, as required for the Software Engineering Lab deliverables.

## 1. Use Case Diagram
Describes the interactions between the users (Admin, Customer) and the system.

```mermaid
useCaseDiagram
    actor Customer
    actor Admin
    
    package "ERP System" {
        usecase "Browse Products" as UC1
        usecase "Add to Cart" as UC2
        usecase "Complete Checkout" as UC3
        usecase "Manage Inventory" as UC4
        usecase "Add New Hardware" as UC5
        usecase "Login/Register" as UC6
    }
    
    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC6
    
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
```

## 2. Software Architecture Diagram
Shows the high-level modular structure of the two integrated subsystems.

```mermaid
graph TD
    subgraph "Web Layer (Flask)"
        UI[User Interface - HTML/CSS]
    end

    subgraph "Inventory Subsystem"
        InvB[Inventory Blueprint]
        StockM[Stock Manager]
    end

    subgraph "Sales Subsystem"
        SalesB[Sales Blueprint]
        CartM[Cart & Order Manager]
    end

    UI <--> InvB
    UI <--> SalesB
    
    SalesB -- "Auto-updates" --> InvB
    InvB <--> DB[(SQLite Database)]
    SalesB <--> DB
```

## 3. Sequence Diagram (Order Flow)
Illustrates the communication between subsystems during a purchase.

```mermaid
sequenceDiagram
    participant User
    participant Sales_Module as Sales Subsystem
    participant Inv_Module as Inventory Subsystem
    participant DB as Database

    User->>Sales_Module: Post Checkout (Address)
    Sales_Module->>DB: Record Order Items
    Sales_Module->>Inv_Module: Trigger Stock Update
    Inv_Module->>DB: UPDATE products SET quantity = quantity - N
    DB-->>Inv_Module: Success
    Inv_Module-->>Sales_Module: Stock Updated
    Sales_Module-->>User: Show Thank You Page (3 Days Delivery)
```

## 4. Entity Relationship Diagram (ERD)
Defines the data structure of the integrated ERP database.

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : included_in
    
    USERS {
        int id PK
        string username
        string email
        string password
        string role
    }
    
    PRODUCTS {
        int id PK
        string name
        string category
        float price
        int quantity
        string image
        string description
    }
    
    ORDERS {
        int id PK
        int user_id FK
        float total_price
        string created_at
        string address
        string status
    }
    
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float price
    }
```

## 5. Class Diagram
Represents the structural model of the modular implementation.

```mermaid
classDiagram
    class Subsystem {
        <<Blueprint>>
    }
    class Inventory {
        +list_products()
        +add_product()
        +delete_product()
        +update_stock(id, diff)
    }
    class Sales {
        +add_to_cart()
        +view_cart()
        +checkout()
    }
    
    Subsystem <|-- Inventory
    Subsystem <|-- Sales
    
    Inventory "1" -- "*" Product : manages
    Sales "1" -- "*" Order : creates
    Order "1" -- "*" OrderItem : contains
    OrderItem "*" -- "1" Product : refers_to
```
