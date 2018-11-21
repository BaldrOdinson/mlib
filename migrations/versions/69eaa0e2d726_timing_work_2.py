"""timing work 2

Revision ID: 69eaa0e2d726
Revises: 7af74e40a153
Create Date: 2018-11-19 19:32:07.392768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69eaa0e2d726'
down_revision = '7af74e40a153'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('methodics', 'timing_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('methodics', 'timing_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
