"""initial_schema

Revision ID: 95a121bf2361
Revises: None
Create Date: 2026-06-19 15:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '95a121bf2361'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 3. Workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('tier', sa.String(), nullable=True),
        sa.Column('prompt_limit', sa.Integer(), nullable=True),
        sa.Column('prompts_used', sa.Integer(), nullable=True),
        sa.Column('api_cost_used', sa.Numeric(10, 6), server_default='0.000000', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Projects
    op.create_table(
        'projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Brands
    op.create_table(
        'brands',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Competitors
    op.create_table(
        'competitors',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('brand_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. AI Models
    op.create_table(
        'ai_models',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Prompts
    op.create_table(
        'prompts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('locale', sa.String(), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. Prompt Runs
    op.create_table(
        'prompt_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('prompt_id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id']),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. Responses
    op.create_table(
        'responses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('prompt_run_id', sa.String(), nullable=False),
        sa.Column('raw_text', sa.String(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('sentiment_score', sa.Numeric(3, 2), nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 6), server_default='0.000000', nullable=True),
        sa.Column('provider_requested', sa.String(), nullable=True),
        sa.Column('provider_used', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['prompt_run_id'], ['prompt_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('prompt_run_id')
    )

    # 11. Domains
    op.create_table(
        'domains',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('domain_authority', sa.Integer(), nullable=True),
        sa.Column('is_competitor', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain')
    )

    # 12. Citation Sources
    op.create_table(
        'citation_sources',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('domain_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )

    # 13. Citations
    op.create_table(
        'citations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('response_id', sa.String(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('is_anchor_citation', sa.Boolean(), nullable=True),
        sa.Column('citation_text', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['response_id'], ['responses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['citation_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. Visibility Scores
    op.create_table(
        'visibility_scores',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('brand_id', sa.String(), nullable=False),
        sa.Column('visibility_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. Visibility History
    op.create_table(
        'visibility_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('brand_id', sa.String(), nullable=False),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('visibility_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('recorded_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['ai_models.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 16. Share of Voice
    op.create_table(
        'share_of_voice',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('brand_id', sa.String(), nullable=True),
        sa.Column('competitor_id', sa.String(), nullable=True),
        sa.Column('share_percentage', sa.Numeric(5, 2), nullable=False),
        sa.Column('recorded_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['competitor_id'], ['competitors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. Recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('estimated_visibility_gain', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 18. Recommendation Actions
    op.create_table(
        'recommendation_actions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('recommendation_id', sa.String(), nullable=False),
        sa.Column('action_text', sa.String(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 19. Agencies
    op.create_table(
        'agencies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('white_label_domain', sa.String(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('custom_colors', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id')
    )

    # 20. Clients
    op.create_table(
        'clients',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('agency_id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('billing_status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workspace_id')
    )

    # 21. Topic Clusters
    op.create_table(
        'topic_clusters',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 22. Topics
    op.create_table(
        'topics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('cluster_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cluster_id'], ['topic_clusters.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 23. Industries
    op.create_table(
        'industries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 24. Industry Rankings
    op.create_table(
        'industry_rankings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('industry_id', sa.String(), nullable=False),
        sa.Column('brand_name', sa.String(), nullable=False),
        sa.Column('visibility_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('weekly_change', sa.Numeric(5, 2), nullable=True),
        sa.Column('ranking', sa.Integer(), nullable=False),
        sa.Column('recorded_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['industry_id'], ['industries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('industry_rankings')
    op.drop_table('industries')
    op.drop_table('topics')
    op.drop_table('topic_clusters')
    op.drop_table('clients')
    op.drop_table('agencies')
    op.drop_table('recommendation_actions')
    op.drop_table('recommendations')
    op.drop_table('share_of_voice')
    op.drop_table('visibility_history')
    op.drop_table('visibility_scores')
    op.drop_table('citations')
    op.drop_table('citation_sources')
    op.drop_table('domains')
    op.drop_table('responses')
    op.drop_table('prompt_runs')
    op.drop_table('prompts')
    op.drop_table('ai_models')
    op.drop_table('competitors')
    op.drop_table('brands')
    op.drop_table('projects')
    op.drop_table('workspaces')
    op.drop_table('users')
    op.drop_table('organizations')
