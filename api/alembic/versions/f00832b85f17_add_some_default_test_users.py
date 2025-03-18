"""add some default test users

Revision ID: f00832b85f17
Revises: 83396d849f66
Create Date: 2025-01-30 01:38:36.340664

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import String
from passlib.context import CryptContext

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f00832b85f17'
down_revision = '83396d849f66'
branch_labels = None
depends_on = None

# Initialize the CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password "devpass"
hashed_password = pwd_context.hash("devpass")

# Define a lightweight table reference for "users"
users_table = table(
    'users',
    column('email', String),
    column('hashed_password', String),
    column('role', ENUM('superadmin', 'admin', 'customer', 'user', name='roleenum', create_type=False))
)

def upgrade() -> None:
    # Insert the default users
    op.bulk_insert(users_table, [
        {
            'email': 'super@admin.com',
            'hashed_password': hashed_password,
            'role': 'superadmin'
        },
        {
            'email': 'admin@admin.com',
            'hashed_password': hashed_password,
            'role': 'admin'
        },
        {
            'email': 'customer@customer.com',
            'hashed_password': hashed_password,
            'role': 'customer'
        },
        {
            'email': 'user@user.com',
            'hashed_password': hashed_password,
            'role': 'user'
        }
    ])

def downgrade() -> None:
    # First delete any tokens associated with the seed users
    op.execute("""
        DELETE FROM tokens 
        WHERE user_id IN (
            SELECT id FROM users 
            WHERE email IN ('super@admin.com', 'admin@admin.com', 'customer@customer.com', 'user@user.com')
        )
    """)
    
    # Then delete the users
    op.execute("DELETE FROM users WHERE email IN ('super@admin.com', 'admin@admin.com', 'customer@customer.com', 'user@user.com')")
