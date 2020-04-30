"""add categories column to table jobs

Revision ID: 3c181ad9c798
Revises: 
Create Date: 2020-04-29 22:25:53.953632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c181ad9c798'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("jobs", sa.Column("categories", sa.types.ARRAY(sa.String)))

def downgrade():
    pass
