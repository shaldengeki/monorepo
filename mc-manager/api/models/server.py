from app import db
import datetime


class Server(db.Model):
    __tablename__ = "servers"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.TIMESTAMP(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    created_by = db.Column(db.Unicode(100), nullable=False)
    name = db.Column(db.Unicode(100), nullable=False, unique=True)
    port = db.Column(db.Integer, nullable=False, unique=True)
    timezone = db.Column(db.Unicode(100), nullable=False)
    zipfile = db.Column(db.Unicode(100), nullable=False)
    motd = db.Column(db.Unicode(100))
    memory = db.Column(db.Unicode(3), nullable=False)
    logs = db.relationship(
        "ServerLog", back_populates="server", order_by="desc(ServerLog.created)"
    )
    backups = db.relationship(
        "ServerBackup", back_populates="server", order_by="desc(ServerBackup.created)"
    )

    def __repr__(self):
        return "<Server {id}>".format(id=self.id)
