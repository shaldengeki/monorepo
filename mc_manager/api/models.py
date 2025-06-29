import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from mc_manager.config import db


class Base(DeclarativeBase):
    pass


class ServerLog(Base):
    __tablename__ = "server_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), primary_key=True)
    backup_id: Mapped[int] = mapped_column(
        ForeignKey("server_backups.id"), primary_key=True
    )
    created: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(String, nullable=False)
    error: Mapped[str]
    server: Mapped["Server"] = relationship(back_populates="logs")
    backup: Mapped["ServerBackup"] = relationship(back_populates="logs")

    def __repr__(self):
        return "<ServerLog {id}>".format(id=self.id)


class ServerBackup(Base):
    __tablename__ = "server_backups"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), primary_key=True)
    created: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(String, nullable=False)
    error: Mapped[str]
    remote_path: Mapped[str] = mapped_column(String, nullable=False)
    server: Mapped["Server"] = relationship(back_populates="backups")
    logs: Mapped["ServerLog"] = relationship(back_populates="backup")

    def __repr__(self):
        return "<ServerBackup {id}>".format(id=self.id)


class Server(Base):
    __tablename__ = "servers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[datetime.datetime] = mapped_column(
        db.TIMESTAMP(timezone=True),
        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        nullable=False,
    )
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    port: Mapped[int] = mapped_column(String, nullable=False, unique=True)
    timezone: Mapped[str] = mapped_column(String, nullable=False)
    zipfile: Mapped[str] = mapped_column(String, nullable=False)
    motd: Mapped[str]
    memory: Mapped[str] = mapped_column(String, nullable=False)

    logs: Mapped["ServerLog"] = relationship(
        back_populates="server", order_by="desc(ServerLog.created)"
    )
    backups: Mapped["ServerBackup"] = relationship(
        back_populates="server", order_by="desc(ServerBackup.created)"
    )

    def __repr__(self):
        return "<Server {id}>".format(id=self.id)
