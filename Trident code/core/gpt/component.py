from dataclasses import field, dataclass


@dataclass
class Component:
    id: int = field(default=None, metadata={"desc": "id"})
    name: str = field(default=None, metadata={"desc": ""})
    text: str = field(default=None, metadata={"desc": "text"})
    resource_id: str = field(default=None, metadata={"desc": "resource id"})
    desc: str = field(default=None, metadata={"desc": "desc"})
    bound: list = field(default=None, metadata={"desc": ""})

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "text": self.text,
            "resource_id": self.resource_id,
            "desc": self.desc,
            "bound": self.bound,
        }
