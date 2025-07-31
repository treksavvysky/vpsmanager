from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = "20250731_160024"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "servers",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("public_ip", sa.String(), nullable=False, unique=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="online"),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("servers")
