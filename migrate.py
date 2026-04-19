#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Migration & Seed Script for Railway PostgreSQL deployment.
Creates all tables and seeds the default admin user.

Run via: python migrate.py
Railway runs this automatically via Procfile release command.
"""

import sys
import os
import io

# Fix Unicode on Windows
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from config import Config
from backend.models import Base, User


def run_migration():
    print("=" * 50)
    print("Starting database migration...")
    print(f"Database URL: {Config.DATABASE_URI[:40]}...")
    print("=" * 50)

    try:
        engine = create_engine(Config.DATABASE_URI)

        # Create all tables (equivalent to init migration)
        print("[1/3] Creating tables...")
        Base.metadata.create_all(engine)
        print("      Tables created successfully.")

        Session = sessionmaker(bind=engine)
        session = Session()

        # Seed default admin user
        print("[2/3] Checking for admin user...")
        admin = session.query(User).filter(User.email == 'admin@example.com').first()

        if not admin:
            print("      Admin not found. Creating default admin...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                # Use werkzeug hash (same as check_password_hash in auth.py)
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            print("      Admin user created:")
            print("        Email:    admin@example.com")
            print("        Password: admin123")
        else:
            # Update existing admin to use werkzeug hash with new password
            print("      Admin found. Updating password hash...")
            admin.password_hash = generate_password_hash('admin123')
            admin.is_admin = True
            admin.is_active = True
            session.commit()
            print("      Admin password updated to: admin123")

        session.close()

        print("[3/3] Migration complete!")
        print("=" * 50)
        print("Login credentials:")
        print("  Email:    admin@example.com")
        print("  Password: admin123")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
