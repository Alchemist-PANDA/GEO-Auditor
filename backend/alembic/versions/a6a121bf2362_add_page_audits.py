"""add page_audits table

Revision ID: a6a121bf2362
Revises: 95a121bf2361
Create Date: 2026-06-20 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a6a121bf2362'
down_revision: Union[str, None] = '95a121bf2361'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'page_audits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('semantic_alignment_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('schema_markup_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('content_structure_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('keyword_stuffing_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='PENDING'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('page_audits')
