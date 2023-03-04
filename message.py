
class Message(object):

    def __init__(self, role, content, success=True) -> None:
        self.role = role
        self.content = content
        self.success = success

    @staticmethod
    def from_dict(data):
        return Message(**data)

    def to_dict(self):
        return dict(role=self.role, content=self.content)
    
    def __repr__(self):
        return f'Message(role={self.role!r}, content={self.content!r})'