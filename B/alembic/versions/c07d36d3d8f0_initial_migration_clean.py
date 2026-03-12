"""initial_migration_clean

Revision ID: c07d36d3d8f0
Revises: 
Create Date: 2026-03-11 20:29:43.522464

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c07d36d3d8f0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Crear tabla roles sin restricciones de llave foránea
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', name='rolestatus'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Crear tabla users sin restricciones de llave foránea
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', name='userstatus'), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 3. Crear tabla sessions
    op.create_table('sessions',
        sa.Column('id', sa.String(length=36), nullable=False), # Cambiado a 36 caracteres
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. AÑADIR LAS LLAVES FORÁNEAS AL FINAL (aquí rompemos el ciclo)
    op.create_foreign_key('fk_roles_updated_by', 'roles', 'users', ['updated_by'], ['id'])
    op.create_foreign_key('fk_roles_deleted_by', 'roles', 'users', ['deleted_by'], ['id'])
    op.create_foreign_key('fk_users_role_id', 'users', 'roles', ['role_id'], ['id'])
    op.create_foreign_key('fk_users_deleted_by', 'users', 'users', ['deleted_by'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_users_deleted_by', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_role_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_roles_deleted_by', 'roles', type_='foreignkey')
    op.drop_constraint('fk_roles_updated_by', 'roles', type_='foreignkey')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('roles')