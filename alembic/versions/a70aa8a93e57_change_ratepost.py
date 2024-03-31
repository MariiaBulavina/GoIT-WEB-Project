"""change RatePost

Revision ID: a70aa8a93e57
Revises: b7a04d79844f
Create Date: 2024-03-30 19:49:34.879666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a70aa8a93e57'
down_revision: Union[str, None] = 'b7a04d79844f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rates_posts', sa.Column('post_id', sa.Integer(), nullable=True))
    op.drop_constraint('rates_posts_photo_id_fkey', 'rates_posts', type_='foreignkey')
    op.create_foreign_key(None, 'rates_posts', 'posts', ['post_id'], ['id'], ondelete='CASCADE')
    op.drop_column('rates_posts', 'photo_id')
    op.alter_column('users', 'user_role',
               existing_type=postgresql.ENUM('admin', 'moderator', 'user', name='user_role'),
               type_=sa.Enum('admin', 'moderator', 'user', name='user_role'),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'user_role',
               existing_type=sa.Enum('admin', 'moderator', 'user', name='user_role'),
               type_=postgresql.ENUM('admin', 'moderator', 'user', name='user_role'),
               existing_nullable=True)
    op.add_column('rates_posts', sa.Column('photo_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'rates_posts', type_='foreignkey')
    op.create_foreign_key('rates_posts_photo_id_fkey', 'rates_posts', 'posts', ['photo_id'], ['id'], ondelete='CASCADE')
    op.drop_column('rates_posts', 'post_id')
    # ### end Alembic commands ###
