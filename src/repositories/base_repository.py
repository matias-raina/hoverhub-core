class BaseRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def add(self, instance):
        self.db_session.add(instance)
        self.db_session.commit()
        return instance

    def get(self, model, id):
        return self.db_session.query(model).filter(model.id == id).first()

    def delete(self, instance):
        self.db_session.delete(instance)
        self.db_session.commit()

    def get_all(self, model):
        return self.db_session.query(model).all()