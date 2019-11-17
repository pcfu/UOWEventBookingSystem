"""add Promotion

Revision ID: f4696a14acf4
Revises: 6ba29a72e8c4
Create Date: 2019-11-18 06:41:17.146831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4696a14acf4'
down_revision = '6ba29a72e8c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('promotion',
    sa.Column('promotion_id', sa.Integer(), nullable=False),
    sa.Column('promo_percentage', sa.Integer(), nullable=False),
    sa.Column('date_start', sa.Date(), nullable=False),
    sa.Column('date_end', sa.Date(), nullable=False),
    sa.Column('promo_code', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('promotion_id', name=op.f('pk_promotion'))
    )
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('promotion_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_payment_promotion_id_promotion'), 'promotion', ['promotion_id'], ['promotion_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_payment_promotion_id_promotion'), type_='foreignkey')
        batch_op.drop_column('promotion_id')

    op.drop_table('promotion')
    # ### end Alembic commands ###
