class Message(object):

    def __init__(self, role, content) -> None:
        self.role = role
        self.content = content

    def to_dict(self):
        return dict(role=self.role, content=self.content)
    
    def __repr__(self):
        return f'Message(role={self.role!r}, content={self.content!r})'