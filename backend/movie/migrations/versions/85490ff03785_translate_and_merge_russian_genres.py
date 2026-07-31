"""translate_and_merge_russian_genres

Revision ID: 85490ff03785
Revises: 07000eff5cd1
Create Date: 2026-07-01 14:30:58.406936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85490ff03785'
down_revision: Union[str, Sequence[str], None] = '07000eff5cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    genre_mapping = {
        "Боевик": "Action",
        "Драма": "Drama",
        "Комедия": "Comedy",
        "Приключения": "Adventure",
        "Триллер": "Thriller",
        "Фантастика": "Sci-Fi"
    }
    
    for ru_name, en_name in genre_mapping.items():
        op.execute(f"""
            DO $$
            DECLARE
                ru_id INT;
                en_id INT;
            BEGIN
                -- Find the Russian genre ID
                SELECT id INTO ru_id FROM genres WHERE name = '{ru_name}';
                
                -- Find the English genre ID
                SELECT id INTO en_id FROM genres WHERE name = '{en_name}';
                
                IF ru_id IS NOT NULL THEN
                    IF en_id IS NULL THEN
                        -- English genre does not exist, simply rename Russian to English
                        UPDATE genres SET name = '{en_name}' WHERE id = ru_id;
                    ELSE
                        -- Both exist, re-link movies from Russian genre to English genre
                        -- First, insert links for movies that don't already have the English genre link
                        INSERT INTO movie_genres (movie_id, genre_id)
                        SELECT movie_id, en_id 
                        FROM movie_genres 
                        WHERE genre_id = ru_id
                        ON CONFLICT DO NOTHING;
                        
                        -- Second, delete all links to the Russian genre
                        DELETE FROM movie_genres WHERE genre_id = ru_id;
                        
                        -- Third, delete the Russian genre itself
                        DELETE FROM genres WHERE id = ru_id;
                    END IF;
                END IF;
            END $$;
        """)


def downgrade() -> None:
    pass
