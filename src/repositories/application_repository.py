class ApplicationRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def submit_application(self, application_data):
        new_application = Application(**application_data)
        self.db_session.add(new_application)
        self.db_session.commit()
        self.db_session.refresh(new_application)
        return new_application

    def get_applications(self, user_id):
        return self.db_session.query(Application).filter(Application.user_id == user_id).all()

    def get_application_by_id(self, application_id):
        return self.db_session.query(Application).filter(Application.id == application_id).first()

    def delete_application(self, application_id):
        application = self.get_application_by_id(application_id)
        if application:
            self.db_session.delete(application)
            self.db_session.commit()
            return True
        return False

    def update_application(self, application_id, updated_data):
        application = self.get_application_by_id(application_id)
        if application:
            for key, value in updated_data.items():
                setattr(application, key, value)
            self.db_session.commit()
            return application
        return None