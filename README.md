
# Real Estate Management System 🏢

A web-based Real Estate Management System designed to handle property listings, client registrations, staff management, and real estate deals. 

This project was built using Python and Flask, integrated with a PostgreSQL.

Disclaimer !!! I used Ai during the work with flask and to connect DB with my python code, it is a new framework for me. Also i consult with AI about FrontEnd part

##  Features

* **Property Management**: Add new properties, view active listings, and safely archive (soft-delete) or restore properties.
* **Client Registry**: Register new clients, categorizing them as either individuals or companies.
* **Staff Directory**: Add new employees and track their roles/positions within the agency.
* **Deal Processing**: Register rental or sale deals. The system uses atomic database transactions to automatically update a property's status (e.g., to "Sold" or "Rented") the moment a deal is logged.
* **Role-Based Workflows**: Dedicated routes for different user roles:
  * **Manager**: Full access to add/view objects, staff, and clients, as well as archive/restore properties.
  * **Realtor**: Access to register deals and manage property transactions.

##  Tech Stack

* **Backend Framework**: Flask
* **Database**: PostgreSQL
* **Database Adapter**: psycopg2
* **Frontend**: HTML Templates
* **Development Tool**: AI-assisted programming
