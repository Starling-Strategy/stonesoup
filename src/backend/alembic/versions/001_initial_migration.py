"""Initial migration with cauldrons, members, and stories tables

Revision ID: 001
Revises: 
Create Date: 2025-07-08 16:00:00.000000

This migration creates the initial database schema for STONESOUP with:
1. Cauldrons table - Multi-tenant organizations/workspaces
2. Members table - User profiles with semantic search capabilities
3. Stories table - Member contributions and achievements
4. Story_members association table - Many-to-many relationship

Key features:
- Multi-tenancy through cauldron_id in all tables
- pgvector extension for semantic search
- HNSW indexes for efficient vector similarity search
- Proper foreign key relationships and constraints
- Comprehensive indexing for performance

Educational Notes:
- HNSW (Hierarchical Navigable Small World) is the preferred algorithm
  for vector similarity search in PostgreSQL with pgvector
- It provides better performance than IVFFlat for high-dimensional vectors
- The m=16 parameter controls the number of connections in the graph
- ef_construction=64 controls the search depth during index construction
- vector_cosine_ops specifies cosine similarity for distance calculations
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create the initial database schema.
    
    This migration creates all tables in the correct order to satisfy
    foreign key dependencies:
    1. Cauldrons (no dependencies)
    2. Members (depends on Cauldrons)
    3. Stories (depends on Cauldrons)
    4. Story_members (depends on Stories and Members)
    """
    
    # Ensure pgvector extension is available
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create cauldrons table
    op.create_table(
        'cauldrons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Display name of the cauldron/organization'),
        sa.Column('slug', sa.String(length=255), nullable=False, comment='URL-friendly identifier for the cauldron'),
        sa.Column('description', sa.Text(), nullable=True, comment='Detailed description of the cauldron\'s purpose and community'),
        sa.Column('configuration', postgresql.JSONB(), nullable=False, comment='JSONB configuration for features, integrations, and settings'),
        sa.Column('global_guidance_prompt', sa.Text(), nullable=True, comment='Global AI prompt that guides how stories are generated and evaluated'),
        sa.Column('embedding_model', sa.String(length=100), nullable=False, comment='The embedding model to use for this cauldron\'s semantic search'),
        sa.Column('features', postgresql.JSONB(), nullable=False, comment='Enabled features for this cauldron (e.g., story_generation, ai_matching)'),
        sa.Column('logo_url', sa.String(), nullable=True, comment='URL to the cauldron\'s logo'),
        sa.Column('primary_color', sa.String(length=7), nullable=True, comment='Primary brand color in hex format'),
        sa.Column('custom_domain', sa.String(), nullable=True, comment='Custom domain for white-label deployments'),
        sa.Column('is_active', sa.Boolean(), nullable=False, comment='Whether the cauldron is currently active'),
        sa.Column('is_public', sa.Boolean(), nullable=False, comment='Whether the cauldron is publicly accessible'),
        sa.Column('member_limit', postgresql.JSONB(), nullable=False, comment='Member limits and current count'),
        sa.Column('story_limit', postgresql.JSONB(), nullable=False, comment='Story limits and current count'),
        sa.Column('subscription_tier', sa.String(length=50), nullable=False, comment='Current subscription tier (free, pro, enterprise)'),
        sa.Column('billing_email', sa.String(), nullable=True, comment='Email for billing communications'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID of the member who owns this cauldron'),
        sa.Column('extra_metadata', postgresql.JSONB(), nullable=False, comment='Additional metadata and custom fields'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('custom_domain'),
        comment='Cauldron model representing an organization/workspace in the talent marketplace'
    )
    
    # Create indexes for cauldrons table
    op.create_index('ix_cauldrons_name', 'cauldrons', ['name'])
    op.create_index('ix_cauldrons_slug', 'cauldrons', ['slug'])
    op.create_index('ix_cauldrons_custom_domain', 'cauldrons', ['custom_domain'])
    op.create_index('ix_cauldrons_is_active', 'cauldrons', ['is_active'])
    op.create_index('ix_cauldrons_owner_id', 'cauldrons', ['owner_id'])
    op.create_index('ix_cauldrons_is_active_is_public', 'cauldrons', ['is_active', 'is_public'])
    op.create_index('ix_cauldrons_subscription_tier', 'cauldrons', ['subscription_tier'])
    op.create_index('ix_cauldrons_features', 'cauldrons', ['features'], postgresql_using='gin')
    op.create_index('ix_cauldrons_extra_metadata', 'cauldrons', ['extra_metadata'], postgresql_using='gin')
    
    # Create members table
    op.create_table(
        'members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('cauldron_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID of the cauldron (organization) this record belongs to'),
        sa.Column('clerk_user_id', sa.String(), nullable=False, comment='Clerk authentication user ID'),
        sa.Column('email', sa.String(), nullable=False, comment='Member\'s email address'),
        sa.Column('name', sa.String(), nullable=False, comment='Member\'s display name'),
        sa.Column('username', sa.String(), nullable=True, comment='Optional username for profile URLs'),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('years_of_experience', sa.Float(), nullable=True),
        sa.Column('hourly_rate', sa.Float(), nullable=True),
        sa.Column('skills', postgresql.JSONB(), nullable=True),
        sa.Column('expertise_areas', postgresql.JSONB(), nullable=True),
        sa.Column('industries', postgresql.JSONB(), nullable=True),
        sa.Column('profile_embedding', Vector(1536), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('profile_completed', sa.Boolean(), nullable=True),
        sa.Column('linkedin_url', sa.String(), nullable=True),
        sa.Column('github_url', sa.String(), nullable=True),
        sa.Column('twitter_url', sa.String(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('portfolio_urls', postgresql.JSONB(), nullable=True),
        sa.Column('extra_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('last_active_at', sa.DateTime(), nullable=True, comment='Last time the member was active on the platform'),
        sa.ForeignKeyConstraint(['cauldron_id'], ['cauldrons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cauldron_id', 'email', name='uq_members_cauldron_email'),
        sa.UniqueConstraint('cauldron_id', 'username', name='uq_members_cauldron_username'),
        sa.UniqueConstraint('cauldron_id', 'clerk_user_id', name='uq_members_cauldron_clerk_user'),
        comment='Member model representing users in the talent marketplace'
    )
    
    # Create indexes for members table
    op.create_index('ix_members_clerk_user_id', 'members', ['clerk_user_id'])
    op.create_index('ix_members_email', 'members', ['email'])
    op.create_index('ix_members_username', 'members', ['username'])
    op.create_index('ix_members_cauldron_id', 'members', ['cauldron_id'])
    op.create_index('ix_members_cauldron_is_active', 'members', ['cauldron_id', 'is_active'])
    op.create_index('ix_members_is_active_is_available', 'members', ['is_active', 'is_available'])
    op.create_index('ix_members_skills', 'members', ['skills'], postgresql_using='gin')
    op.create_index('ix_members_expertise_areas', 'members', ['expertise_areas'], postgresql_using='gin')
    op.create_index('ix_members_industries', 'members', ['industries'], postgresql_using='gin')
    
    # Create HNSW index for member profile embeddings
    # This is the key index for semantic search of member profiles
    op.create_index(
        'ix_members_profile_embedding_hnsw',
        'members',
        ['profile_embedding'],
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'profile_embedding': 'vector_cosine_ops'}
    )
    
    # Create stories table
    op.create_table(
        'stories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('cauldron_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID of the cauldron (organization) this record belongs to'),
        sa.Column('title', sa.String(length=255), nullable=False, comment='Story title for display and search'),
        sa.Column('content', sa.Text(), nullable=False, comment='Full story content in markdown format'),
        sa.Column('summary', sa.Text(), nullable=True, comment='Brief summary for previews and search results'),
        sa.Column('story_type', sa.Enum('ACHIEVEMENT', 'EXPERIENCE', 'SKILL_DEMONSTRATION', 'TESTIMONIAL', 'CASE_STUDY', 'THOUGHT_LEADERSHIP', name='storytype'), nullable=False, comment='Type of story for categorization'),
        sa.Column('status', sa.Enum('DRAFT', 'PENDING_REVIEW', 'PUBLISHED', 'ARCHIVED', 'REJECTED', name='storystatus'), nullable=False, comment='Current status in the publication lifecycle'),
        sa.Column('embedding', Vector(1536), nullable=True, comment='Vector embedding for semantic search (1536 dims for OpenAI)'),
        sa.Column('confidence_score', sa.Float(), nullable=True, comment='AI confidence score (0-1) for generated content'),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, comment='Whether this story was generated by AI'),
        sa.Column('generation_prompt', sa.Text(), nullable=True, comment='The prompt used to generate this story (if AI-generated)'),
        sa.Column('tags', postgresql.JSONB(), nullable=False, comment='Array of tags for categorization'),
        sa.Column('skills_demonstrated', postgresql.JSONB(), nullable=False, comment='Skills showcased in this story'),
        sa.Column('occurred_at', sa.DateTime(), nullable=True, comment='When the story event occurred (different from created_at)'),
        sa.Column('published_at', sa.DateTime(), nullable=True, comment='When the story was published'),
        sa.Column('external_url', sa.String(), nullable=True, comment='Link to external content (portfolio, article, etc.)'),
        sa.Column('company', sa.String(), nullable=True, comment='Company/organization associated with the story'),
        sa.Column('view_count', sa.Integer(), nullable=False, comment='Number of times the story has been viewed'),
        sa.Column('like_count', sa.Integer(), nullable=False, comment='Number of likes/endorsements'),
        sa.Column('reviewed_by_id', postgresql.UUID(as_uuid=True), nullable=True, comment='ID of the member who reviewed this story'),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True, comment='When the story was reviewed'),
        sa.Column('review_notes', sa.Text(), nullable=True, comment='Internal notes from the review process'),
        sa.Column('extra_metadata', postgresql.JSONB(), nullable=False, comment='Additional flexible metadata'),
        sa.ForeignKeyConstraint(['cauldron_id'], ['cauldrons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by_id'], ['members.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='Story model representing contributions and achievements in the talent marketplace'
    )
    
    # Create indexes for stories table
    op.create_index('ix_stories_title', 'stories', ['title'])
    op.create_index('ix_stories_story_type', 'stories', ['story_type'])
    op.create_index('ix_stories_status', 'stories', ['status'])
    op.create_index('ix_stories_published_at', 'stories', ['published_at'])
    op.create_index('ix_stories_company', 'stories', ['company'])
    op.create_index('ix_stories_cauldron_id', 'stories', ['cauldron_id'])
    op.create_index('ix_stories_cauldron_status', 'stories', ['cauldron_id', 'status'])
    op.create_index('ix_stories_cauldron_type', 'stories', ['cauldron_id', 'story_type'])
    op.create_index('ix_stories_tags', 'stories', ['tags'], postgresql_using='gin')
    op.create_index('ix_stories_skills', 'stories', ['skills_demonstrated'], postgresql_using='gin')
    op.create_index('ix_stories_ai_generated', 'stories', ['ai_generated'])
    
    # Create HNSW index for story embeddings
    # This enables semantic search across all story content
    op.create_index(
        'ix_stories_embedding_hnsw',
        'stories',
        ['embedding'],
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'embedding': 'vector_cosine_ops'}
    )
    
    # Create story_members association table
    op.create_table(
        'story_members',
        sa.Column('story_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('member_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cauldron_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Cauldron ID for multi-tenancy - must match both story and member cauldron_id'),
        sa.Column('role', sa.String(), nullable=True, comment='Member\'s role in the story (e.g., \'author\', \'contributor\')'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cauldron_id'], ['cauldrons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('story_id', 'member_id'),
        comment='Association table for many-to-many relationship between stories and members'
    )
    
    # Create indexes for story_members table
    op.create_index('ix_story_members_story_id', 'story_members', ['story_id'])
    op.create_index('ix_story_members_member_id', 'story_members', ['member_id'])
    op.create_index('ix_story_members_cauldron_id', 'story_members', ['cauldron_id'])


def downgrade() -> None:
    """
    Drop all tables in reverse order to respect foreign key constraints.
    
    Note: This will permanently delete all data. Use with extreme caution.
    """
    op.drop_table('story_members')
    op.drop_table('stories')
    op.drop_table('members')
    op.drop_table('cauldrons')
    
    # Drop custom enum types
    op.execute("DROP TYPE IF EXISTS storytype")
    op.execute("DROP TYPE IF EXISTS storystatus")