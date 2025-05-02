"""add_portuguese_text_fields

Revision ID: d928a76a14cb
Revises: 399b570eab29
Create Date: 2025-05-02 13:48:29.250273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd928a76a14cb'
down_revision: Union[str, None] = '399b570eab29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('title_pt', sa.String(255), nullable=True))
    op.add_column('posts', sa.Column('content_pt', sa.Text(), nullable=True))
    op.add_column('posts', sa.Column('summary_pt', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'title_pt')
    op.drop_column('posts', 'content_pt')
    op.drop_column('posts', 'summary_pt')
