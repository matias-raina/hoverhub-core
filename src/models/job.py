class Job:
    def __init__(self, id: int, title: str, description: str, user_id: int):
        self.id = id
        self.title = title
        self.description = description
        self.user_id = user_id

    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, user_id={self.user_id})>"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            user_id=data.get("user_id"),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
        }