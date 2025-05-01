"""msg=Seed preset author

Revision ID: 399b570eab29
Revises: 
Create Date: 2025-05-01 10:32:20.468897

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import table, column, String, Text, Boolean # Import necessary types
from sqlalchemy.sql import select, insert, delete # Import specific SQL functions

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '399b570eab29' # Match the filename
down_revision: Union[str, None] = None # Match the previous revision
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the preset author details
# CHANGE THESE VALUES TO YOUR DESIRED PRESET AUTHOR
PRESET_AUTHOR_NAME = "h0ffmann"
PRESET_AUTHOR_EMAIL = "hoffmann@poli.ufrj.br" # Use a unique email!
PRESET_AUTHOR_BIO = "The default administrator account for hoffmagic."
PRESET_AUTHOR_AVATAR = "https://avatars.githubusercontent.com/u/17460827?v=4" # Or provide a default URL, e.g., "/static/images/avatars/default_admin.png"

# Define the table structure minimally for the operations
# It's generally better to define the table structure explicitly here rather
# than importing the model directly to avoid potential circular dependencies
# or issues if the model changes significantly later.
authors_table = table(
    "authors", # Table name must match your database
    column("id", sa.Integer), # Need id for reflection but don't insert it
    column("name", String),
    column("email", String),
    column("bio", Text),
    column("avatar", String),
    # Add any other NOT NULL columns without defaults here if necessary
    # You don't need to define columns you aren't interacting with or that have defaults
)


def upgrade() -> None:
    """Add the preset author if they don't exist."""
    bind = op.get_bind() # Get the current database connection

    # --- Check if the author already exists ---
    select_stmt = select(authors_table.c.id).where(authors_table.c.email == PRESET_AUTHOR_EMAIL)
    result = bind.execute(select_stmt).scalar_one_or_none()

    if result:
        # Author already exists, do nothing
        print(f"Author with email {PRESET_AUTHOR_EMAIL} already exists. Skipping insertion.")
    else:
        # Author does not exist, insert them
        print(f"Inserting preset author {PRESET_AUTHOR_NAME} ({PRESET_AUTHOR_EMAIL}).")
        op.bulk_insert(
            authors_table,
            [
                {
                    'name': PRESET_AUTHOR_NAME,
                    'email': PRESET_AUTHOR_EMAIL,
                    'bio': PRESET_AUTHOR_BIO,
                    'avatar': PRESET_AUTHOR_AVATAR,
                }
            ]
        )
        # Alternative using insert statement (slightly more verbose but explicit):
        # insert_stmt = insert(authors_table).values(
        #     name=PRESET_AUTHOR_NAME,
        #     email=PRESET_AUTHOR_EMAIL,
        #     bio=PRESET_AUTHOR_BIO,
        #     avatar=PRESET_AUTHOR_AVATAR,
        # )
        # bind.execute(insert_stmt)


def downgrade() -> None:
    """Remove the preset author if they exist (optional)."""
    # Downgrading seed data can be tricky if the data might have been modified.
    # Often, you might just 'pass' in the downgrade for seed migrations.
    # However, attempting deletion by email is relatively safe.

    bind = op.get_bind()
    delete_stmt = delete(authors_table).where(authors_table.c.email == PRESET_AUTHOR_EMAIL)

    print(f"Attempting to remove preset author {PRESET_AUTHOR_NAME} ({PRESET_AUTHOR_EMAIL}).")
    result = bind.execute(delete_stmt)

    if result.rowcount > 0:
        print(f"Removed preset author with email {PRESET_AUTHOR_EMAIL}.")
    else:
        print(f"Preset author with email {PRESET_AUTHOR_EMAIL} not found for removal.")

    # If you prefer not to attempt removal, uncomment the line below and remove the rest:
    # pass