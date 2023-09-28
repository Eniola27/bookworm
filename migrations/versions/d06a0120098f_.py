"""empty message

Revision ID: d06a0120098f
Revises: 
Create Date: 2023-09-20 14:05:34.463963

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd06a0120098f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contactus',
    sa.Column('contact_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('contact_email', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('contact_id')
    )
    op.create_table('state',
    sa.Column('state_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('state_name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('state_id')
    )
    op.create_table('lga',
    sa.Column('lga_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('state_id', sa.Integer(), nullable=False),
    sa.Column('lga_name', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['state_id'], ['state.state_id'], ),
    sa.PrimaryKeyConstraint('lga_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lga')
    op.drop_table('state')
    op.drop_table('contactus')
    # ### end Alembic commands ###