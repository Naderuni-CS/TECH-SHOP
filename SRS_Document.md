# Software Requirements Specification (SRS)
## Project: Computer Shop ERP System

### 1. Introduction
#### 1.1 Purpose
The purpose of this document is to define the functional and non-functional requirements for the Computer Shop ERP System. This system is designed as a mini ERP project for a Software Engineering Lab, consisting of two integrated subsystems: Inventory and Sales.

#### 1.2 Scope
The system allows administrators to manage inventory (laptops, accessories) and users to browse and purchase hardware. The system ensures that sales transactions automatically update the inventory levels.

### 2. Overall Description
#### 2.1 Product Perspective
The system is a standalone web application built with Python (Flask), SQLite, and Vanilla CSS. It provides a modular architecture where Sales and Inventory functions are separated but integrated.

#### 2.2 System Functions
- **Inventory Management**: Add, view, and delete products.
- **Stock Tracking**: Monitor quantities and low-stock alerts.
- **User Management**: Registration and login for customers.
- **Order Management**: Shopping cart, address collection, and checkout.
- **Automated Communication**: Sales system triggers inventory decrement.

### 3. Functional Requirements

| ID | Feature | Description |
| :--- | :--- | :--- |
| FR-01 | Product Management | Admin can add new products with images and categories. |
| FR-02 | Inventory Tracking | System displays real-time stock levels for all hardware. |
| FR-03 | Cart System | Users can add multiple items to a digital cart with count badge. |
| FR-04 | Secure Checkout | Users must provide a shipping address to place an order. |
| FR-05 | Auto-Stock Update | Checkout process automatically decrements quantity from Inventory Subsystem. |
| FR-06 | Admin Dashboard | A dedicated panel for managing stock and product visibility. |

### 4. Non-Functional Requirements
- **Performance**: Page loads must be fast to ensure a premium user experience.
- **Security**: Passwords must be hashed using industry-standard algorithms (PBKDF2).
- **Usability**: The interface must be modern, tech-focused, and mobile-responsive.
- **Integrity**: Database transactions must be atomic (decrement stock only if order is successful).

### 5. Design Constraints
- Technology Stack: Python 3.x, Flask, SQLite3, CSS3.
- Modular Design: System must be split into integrated subsystems.
