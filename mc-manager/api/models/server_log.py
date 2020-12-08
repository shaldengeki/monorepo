from ..app import db
from .server import Server


class ServerLog(db.Model):
    __tablename__ = "server_logs"
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey(Server.id), nullable=False)
    created = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    state = db.Column(db.Unicode(100), nullable=False)
    error = db.Column(db.Unicode(500), nullable=True)
    server = db.relationship("Server", back_populates="logs")

    def __repr__(self):
        return "<ServerLog {id}>".format(id=self.id)
