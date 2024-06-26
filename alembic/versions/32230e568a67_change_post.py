"""change post

Revision ID: 32230e568a67
Revises: ba5abf23160c
Create Date: 2024-03-24 22:55:37.718516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '32230e568a67'
down_revision: Union[str, None] = 'ba5abf23160c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('post_url', sa.String(), nullable=True))
    op.add_column('posts', sa.Column('public_id', sa.String(), nullable=True))
    op.drop_column('posts', 'photo_url')
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
    op.add_column('posts', sa.Column('photo_url', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('posts', 'public_id')
    op.drop_column('posts', 'post_url')
    # ### end Alembic commands ###
