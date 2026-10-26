"""add user email

Revision ID: 5b1c9d2e7a10
Revises: 38c4e85512a9
Create Date: 2026-10-26 12:00:00.000000

"""

# revision identifiers, used by Alembic.
revision = '5b1c9d2e7a10'
down_revision = '38c4e85512a9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('email', sa.String(length=120), nullable=True))


def downgrade():
    op.drop_column('users', 'email')
