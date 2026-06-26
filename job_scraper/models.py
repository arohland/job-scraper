from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Job:
    title: str
    site: str
    link: str
    deadline: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    llm_relevant: Optional[bool] = None
    llm_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Job":
        known_fields = Job.__dataclass_fields__
        return Job(**{k: v for k, v in data.items() if k in known_fields})
