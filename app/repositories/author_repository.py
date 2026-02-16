from app.db.models.author import Author
from app.repositories.base import Repository


author_repository = Repository[Author](Author)

