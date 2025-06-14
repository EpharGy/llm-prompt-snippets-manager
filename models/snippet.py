from dataclasses import dataclass
from typing import List
import uuid

@dataclass
class Snippet:
    id: str
    name: str
    category: str
    prompt_text: str
    labels: List[str]
    exclusive: bool

    @classmethod
    def create(cls, name: str, category: str, prompt_text: str, labels: List[str], exclusive: bool):
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            category=category,
            prompt_text=prompt_text,
            labels=labels,
            exclusive=exclusive
        )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "prompt_text": self.prompt_text,
            "labels": self.labels,
            "exclusive": self.exclusive
        }

    def matches_search(self, search_terms: List[str]) -> bool:
        """Check if snippet matches all search terms"""
        searchable_text = (
            f"{self.name} {' '.join(self.labels)} {self.category} {self.prompt_text}"
        ).lower()
        return all(term in searchable_text for term in search_terms)