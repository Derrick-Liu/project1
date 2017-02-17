"""empty message

Revision ID: 5bdcb7596179
Revises: e13f204cefc9
Create Date: 2016-11-25 17:07:49.103000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bdcb7596179'
down_revision = 'e13f204cefc9'
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('address', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('date_of_born', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=32), nullable=True))
    op.drop_index('ix_users_email', table_name='users')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_users_email', 'users', ['email'], unique=1)
    op.drop_column('users', 'gender')
    op.drop_column('users', 'date_of_born')
    op.drop_column('users', 'address')
    ### end Alembic commands ###