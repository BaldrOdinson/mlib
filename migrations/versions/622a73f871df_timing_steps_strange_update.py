"""timing_steps strange update

Revision ID: 622a73f871df
Revises: 9c32d5d2b94b
Create Date: 2018-12-06 17:03:26.315089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '622a73f871df'
down_revision = '9c32d5d2b94b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('timing_steps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('method_timing_id', sa.Integer(), nullable=False),
    sa.Column('step_duration', sa.Integer(), nullable=False),
    sa.Column('step_desc', sa.Text(), nullable=False),
    sa.Column('step_result', sa.Text(), nullable=False),
    sa.Column('step_label_image', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['method_timing_id'], ['method_timing.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('timing_steps')
    # ### end Alembic commands ###
