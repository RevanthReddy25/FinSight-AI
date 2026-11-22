from alembic import op
import sqlalchemy as sa


def upgrade():

    op.create_table(
        "transactions",

        sa.Column(
            "transaction_id",
            sa.Integer,
            primary_key=True
        ),

        sa.Column(
            "amount",
            sa.Numeric(12, 2),
            nullable=False
        ),

        sa.Column(
            "category",
            sa.String(100),
            nullable=False
        )
    )


def downgrade():

    op.drop_table("transactions")