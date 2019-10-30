"""event: venue_id changed to non-nullable

Revision ID: aac55322d2c5
Revises: b2b735b54bb4
Create Date: 2019-10-30 08:27:30.838845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aac55322d2c5'
down_revision = 'b2b735b54bb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###