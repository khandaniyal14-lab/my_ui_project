"""
Seed Companies Script

This script creates the companies database and populates it with sample data.
It uses the Company model defined in app.py.

Usage:
    python seed_companies.py
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import random

# Create a minimal Flask app for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///companies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Company model (same as in app.py)
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    address = db.Column(db.String(300))
    phone = db.Column(db.String(50))
    mobile = db.Column(db.String(50))
    email = db.Column(db.String(100))
    services = db.Column(db.String(300))

# Sample data for seeding the database
sample_companies = [
    {
        "name": "Karachi Textile Mills",
        "address": "www.karachitextile.com",
        "phone": "+92 21 34567890",
        "mobile": "+92 300 1234567",
        "email": "info@karachitextile.com",
        "services": "Yarn manufacturing, Fabric processing, Dyeing services, Cotton exports"
    },
    {
        "name": "Punjab Rice Traders",
        "address": "www.punjabrice.com.pk",
        "phone": "+92 42 37373737",
        "mobile": "+92 321 1122334",
        "email": "export@punjabrice.com.pk",
        "services": "Basmati rice, Parboiled rice, Packaging, Global exports"
    },
    {
        "name": "Sialkot Sports Gear",
        "address": "www.sialkotsportsgear.com",
        "phone": "+92 52 4267890",
        "mobile": "+92 332 4567890",
        "email": "sales@sialkotsportsgear.com",
        "services": "Football manufacturing, Sports gloves, Cricket gear, OEM supplies"
    },
    {
        "name": "Lahore Leather Works",
        "address": "www.lahoreleather.pk",
        "phone": "+92 42 35900011",
        "mobile": "+92 300 9988776",
        "email": "orders@lahoreleather.pk",
        "services": "Tanned leather, Leather bags, Footwear, Custom accessories"
    },
    {
        "name": "Multan Blue Pottery",
        "address": "www.multanpottery.com",
        "phone": "+92 61 6789012",
        "mobile": "+92 333 6655443",
        "email": "contact@multanpottery.com",
        "services": "Handcrafted ceramics, Blue pottery, Souvenirs, Decorative tiles"
    },
    {
        "name": "Pak Agro Foods",
        "address": "www.pakagrofoods.com",
        "phone": "+92 21 38475632",
        "mobile": "+92 302 1112233",
        "email": "info@pakagrofoods.com",
        "services": "Fruits and vegetables, Dates, Organic spices, Halal food exports"
    },
    {
        "name": "Quetta Marble Industries",
        "address": "www.quettamarble.com",
        "phone": "+92 81 2828374",
        "mobile": "+92 312 4567890",
        "email": "support@quettamarble.com",
        "services": "Marble tiles, Stone blocks, Floor slabs, Export logistics"
    },
    {
        "name": "Islamabad IT Solutions",
        "address": "www.isbit.com.pk",
        "phone": "+92 51 5551234",
        "mobile": "+92 344 2223344",
        "email": "support@isbit.com.pk",
        "services": "Web development, ERP systems, Cybersecurity, Mobile app design"
    },
    {
        "name": "Faisalabad Garment Hub",
        "address": "www.faisalgarments.com",
        "phone": "+92 41 8789090",
        "mobile": "+92 300 5678901",
        "email": "export@faisalgarments.com",
        "services": "T-shirts, Jeans, Kidswear, Global B2B supply"
    },
    {
        "name": "Hyderabad Handicrafts",
        "address": "www.hyderabadcrafts.pk",
        "phone": "+92 22 2783002",
        "mobile": "+92 301 5566778",
        "email": "hello@hyderabadcrafts.pk",
        "services": "Traditional Sindhi crafts, Embroidery, Cultural decor, Hand-woven products"
    },
    {
        "name": "Kigali Coffee Exporters",
        "address": "www.kigalicoffee.rw",
        "phone": "+250 788 123456",
        "mobile": "+250 722 334455",
        "email": "info@kigalicoffee.rw",
        "services": "Arabica beans, Specialty coffee, Organic coffee, Direct trade"
    },
    {
        "name": "Rwanda Tech Innovations",
        "address": "www.rwandatech.rw",
        "phone": "+250 786 567890",
        "mobile": "+250 733 445566",
        "email": "contact@rwandatech.rw",
        "services": "Custom software, IT training, Web platforms, Business automation"
    },
    {
        "name": "Nyungwe Herbal Exports",
        "address": "www.nyungweherbs.rw",
        "phone": "+250 783 112233",
        "mobile": "+250 722 554433",
        "email": "sales@nyungweherbs.rw",
        "services": "Herbal teas, Medicinal plants, Dried leaves, Natural oils"
    },
    {
        "name": "Volcano Leather Works",
        "address": "www.volcanoleather.rw",
        "phone": "+250 789 665544",
        "mobile": "+250 721 123456",
        "email": "orders@volcanoleather.rw",
        "services": "Leather bags, Handmade belts, Wallets, Artisanal goods"
    },
    {
        "name": "Akagera Honey Co.",
        "address": "www.akagerahoney.rw",
        "phone": "+250 788 998877",
        "mobile": "+250 734 556677",
        "email": "support@akagerahoney.rw",
        "services": "Raw honey, Beeswax, Beekeeping products, Agro exports"
    },
    {
        "name": "Rwanda Agri Traders",
        "address": "www.rwandaagri.rw",
        "phone": "+250 782 445566",
        "mobile": "+250 722 998877",
        "email": "info@rwandaagri.rw",
        "services": "Beans, Maize, Horticulture, Organic farming"
    },
    {
        "name": "Lake Kivu Fish Co.",
        "address": "www.lakekivufish.rw",
        "phone": "+250 783 223344",
        "mobile": "+250 735 112233",
        "email": "export@lakekivufish.rw",
        "services": "Tilapia, Processed fish, Cold storage, Regional distribution"
    },
    {
        "name": "Kigali Fashion Studio",
        "address": "www.kigalifashion.rw",
        "phone": "+250 787 345678",
        "mobile": "+250 723 345678",
        "email": "contact@kigalifashion.rw",
        "services": "Tailoring, Traditional wear, African prints, Custom clothing"
    },
    {
        "name": "Rwanda Green Energy Ltd",
        "address": "www.rwandagreenenergy.rw",
        "phone": "+250 781 334455",
        "mobile": "+250 720 998822",
        "email": "hello@rwandagreenenergy.rw",
        "services": "Solar panels, Mini-grids, Sustainable lighting, Energy consulting"
    },
    {
        "name": "Muhanga Ceramic Works",
        "address": "www.muhangaceramics.rw",
        "phone": "+250 789 112244",
        "mobile": "+250 722 998877",
        "email": "support@muhangaceramics.rw",
        "services": "Clay pottery, Roofing tiles, Brick production, Custom ceramic ware"
    }
]




def create_db():
    """Create the database and tables"""
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database tables created successfully.")

def seed_companies():
    """Seed the database with sample companies"""
    with app.app_context():
        # Check if companies already exist
        existing_count = Company.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} companies.")
            choice = input("Do you want to add more companies? (y/n): ").lower()
            if choice != 'y':
                return
        
        # Add sample companies
        for company_data in sample_companies:
            company = Company(**company_data)
            db.session.add(company)
        
        # Commit changes
        db.session.commit()
        print(f"Added {len(sample_companies)} sample companies to the database.")

def main():
    """Main function to create and seed the database"""
    print("Starting database creation and seeding process...")
    
    # Create database and tables
    create_db()
    
    # Seed with sample data
    seed_companies()
    
    print("Database creation and seeding completed successfully!")

if __name__ == "__main__":
    main()
