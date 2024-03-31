"""change post

Revision ID: 07771d06b21c
Revises: c5beec8fa6db
Create Date: 2024-03-31 04:41:50.394360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '07771d06b21c'
down_revision: Union[str, None] = 'c5beec8fa6db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
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
    # ### end Alembic commands ###
