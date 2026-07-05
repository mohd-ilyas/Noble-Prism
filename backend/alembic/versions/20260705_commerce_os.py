from alembic import op
import sqlalchemy as sa

revision = "20260705_commerce_os"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "provider_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider_name", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("region", sa.String(length=64), nullable=False),
        sa.Column("price_per_unit", sa.Float(), nullable=False),
        sa.Column("sla_days", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("reputation_score", sa.Float(), nullable=False),
        sa.Column("sustainability_score", sa.Float(), nullable=False),
        sa.Column("availability", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_name"),
    )
    op.create_table(
        "automation_workflows",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("selected_provider", sa.String(length=128), nullable=True),
        sa.Column("workflow_summary", sa.Text(), nullable=False),
        sa.Column("approval_required", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "negotiation_quotes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_id", sa.String(length=36), nullable=False),
        sa.Column("provider_id", sa.String(length=36), nullable=True),
        sa.Column("provider_name", sa.String(length=128), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("sla_days", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("reputation_score", sa.Float(), nullable=False),
        sa.Column("sustainability_score", sa.Float(), nullable=False),
        sa.Column("decision_score", sa.Float(), nullable=False),
        sa.Column("counter_offer", sa.Text(), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["workflow_id"], ["automation_workflows.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_id"], ["provider_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "workflow_steps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_id", sa.String(length=36), nullable=False),
        sa.Column("step_name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["workflow_id"], ["automation_workflows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("workflow_steps")
    op.drop_table("negotiation_quotes")
    op.drop_table("automation_workflows")
    op.drop_table("provider_profiles")
