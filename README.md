
# Real Estate Management System 🏢

A web-based Real Estate Management System designed to handle property listings, client registrations, staff management, and real estate deals. 

This project was built using **Python** and **Flask**, integrated with a PostgreSQL database using **`psycopg2`**. The development of this application was accelerated and assisted by **AI**.
Disclaimer !!! I used Ai during the work with flask, it is a new framework for me
## ✨ Features

* **Property Management**: Add new properties, view active listings, and safely archive (soft-delete) or restore properties.
* **Client Registry**: Register new clients, categorizing them as either individuals or companies.
* **Staff Directory**: Add new employees and track their roles/positions within the agency.
* **Deal Processing**: Register rental or sale deals. The system uses atomic database transactions to automatically update a property's status (e.g., to "Sold" or "Rented") the moment a deal is logged.
* **Role-Based Workflows**: Dedicated routes for different user roles:
  * **Manager**: Full access to add/view objects, staff, and clients, as well as archive/restore properties.
  * **Realtor**: Access to register deals and manage property transactions.

## 🛠️ Tech Stack

* **Backend Framework**: [Flask](https://flask.palletsprojects.com/) (Python)
* **Database**: PostgreSQL
* **Database Adapter**: `psycopg2`
* **Frontend**: HTML/Jinja2 Templates
* **Development Tool**: AI-assisted programming
