from alembic import op
import sqlalchemy as sa


# Идентификаторы миграций Alembic
revision = "0001_add_organization_topic"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organization_topic",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("topic_num", sa.Integer(), nullable=False),
        sa.Column("coefficient", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"]),
        sa.ForeignKeyConstraint(["topic_num"], ["topic.num"]),
        sa.PrimaryKeyConstraint("organization_id", "topic_num"),
    )


def downgrade() -> None:
    op.drop_table("organization_topic")

