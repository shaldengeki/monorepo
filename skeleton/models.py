from sqlalchemy.orm import Mapped, mapped_column

from skeleton.config import db


class ExampleModel(db.Model):
    __tablename__ = "example_models"
    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f"<{self.__name__} {self.fitbit_user_id}>"
