"""add payment model

Revision ID: da87bad07e28
Revises: 19917246b7ea
Create Date: 2019-11-05 23:05:57.102655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da87bad07e28'
down_revision = '19917246b7ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payment',
    sa.Column('payment_id', sa.Integer(), nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('card_number', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.booking_no'], name=op.f('fk_payment_booking_id_booking')),
    sa.PrimaryKeyConstraint('payment_id', name=op.f('pk_payment'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payment')
    # ### end Alembic commands ###
