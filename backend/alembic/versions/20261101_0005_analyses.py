"""analyses

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '0005'
down_revision: str | None = '0004'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('analyses',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('resume_id', sa.Uuid(), nullable=False),
    sa.Column('job_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('input_hash', sa.String(length=64), nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('pending', 'running', 'done', 'failed')", name=op.f('ck_analyses_status_valid')),
    sa.CheckConstraint('score IS NULL OR (score BETWEEN 0 AND 100)', name=op.f('ck_analyses_score_range')),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], name=op.f('fk_analyses_job_id_jobs'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], name=op.f('fk_analyses_resume_id_resumes'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_analyses_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_analyses'))
    )
    op.create_index(op.f('ix_analyses_job_id'), 'analyses', ['job_id'], unique=False)
    op.create_index(op.f('ix_analyses_resume_id'), 'analyses', ['resume_id'], unique=False)
    op.create_index(op.f('ix_analyses_user_id'), 'analyses', ['user_id'], unique=False)
    op.create_index('ix_analyses_user_id_input_hash', 'analyses', ['user_id', 'input_hash'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_analyses_user_id_input_hash', table_name='analyses')
    op.drop_index(op.f('ix_analyses_user_id'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_resume_id'), table_name='analyses')
    op.drop_index(op.f('ix_analyses_job_id'), table_name='analyses')
    op.drop_table('analyses')
