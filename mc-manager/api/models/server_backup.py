import datetime

from ..config import db
from .server import Server


class ServerBackup(db.Model):
    __tablename__ = "server_backups"
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey(Server.id), nullable=False)
    created = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    state = db.Column(db.Unicode(100), nullable=False)
    error = db.Column(db.Unicode(500), nullable=True)
    remote_path = db.Column(db.Unicode(500), nullable=False)
    server = db.relationship("Server", back_populates="backups")
    logs = db.relationship("ServerLog", back_populates="backup")

    def __repr__(self):
        return "<ServerBackup {id}>".format(id=self.id)
