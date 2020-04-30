"""add tags column to table jobs

Revision ID: ee87f8bd6c1e
Revises: 3c181ad9c798
Create Date: 2020-04-29 22:48:42.145710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee87f8bd6c1e'
down_revision = '3c181ad9c798'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("jobs", sa.Column("tags", sa.types.ARRAY(sa.String)))


def downgrade():
    pass
