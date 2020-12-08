from ..app import db
from .server_log import ServerLog


class Server(db.Model):
    __tablename__ = "servers"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    created_by = db.Column(db.Unicode(100), nullable=False)
    name = db.Column(db.Unicode(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    timezone = db.Column(db.Unicode(100), nullable=False)
    zipfile = db.Column(db.Unicode(100), nullable=False)
    motd = db.Column(db.Unicode(100))
    memory = db.Column(db.Unicode(3), nullable=False)

    def __repr__(self):
        return "<Server {id}>".format(id=self.id)
