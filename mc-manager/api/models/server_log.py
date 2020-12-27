import datetime

from ..app import db
from .server import Server
from .server_backup import ServerBackup


class ServerLog(db.Model):
    __tablename__ = "server_logs"
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey(Server.id), nullable=False)
    created = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    state = db.Column(db.Unicode(100), nullable=False)
    error = db.Column(db.Unicode(500), nullable=True)
    backup_id = db.Column(db.Integer, db.ForeignKey(ServerBackup.id), nullable=True)
    server = db.relationship("Server", back_populates="logs")
    backup = db.relationship("ServerBackup", back_populates="server_logs")

    def __repr__(self):
        return "<ServerLog {id}>".format(id=self.id)
