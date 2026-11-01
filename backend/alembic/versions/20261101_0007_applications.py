"""applications

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-01 15:11:34.205626
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '0007'
down_revision: str | None = '0006'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('applications',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('job_id', sa.Uuid(), nullable=False),
    sa.Column('analysis_id', sa.Uuid(), nullable=True),
    sa.Column('platform', sa.String(length=60), nullable=True),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('salary_expectation', sa.Integer(), nullable=True),
    sa.Column('next_step', sa.String(length=300), nullable=True),
    sa.Column('applied_at', sa.Date(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('sent', 'in_review', 'tech_test', 'interview', 'offer', 'rejected', 'no_response')", name=op.f('ck_applications_status_valid')),
    sa.CheckConstraint('salary_expectation IS NULL OR salary_expectation >= 0', name=op.f('ck_applications_salary_non_negative')),
    sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], name=op.f('fk_applications_analysis_id_analyses'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], name=op.f('fk_applications_job_id_jobs'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_applications_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_applications')),
    sa.UniqueConstraint('job_id', name=op.f('uq_applications_job_id'))
    )
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_table('applications')
