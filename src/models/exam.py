from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExamDownload:
    exam_url: Optional[str] = None
    answer_key_url: Optional[str] = None


@dataclass
class Exam:
    name: str
    year: str
    organization: str
    institution: str
    level: str
    page_url: str
    download: ExamDownload = field(default_factory=ExamDownload)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "year": self.year,
            "organization": self.organization,
            "institution": self.institution,
            "level": self.level,
            "page_url": self.page_url,
            "download": {
                "exam_url": self.download.exam_url,
                "answer_key_url": self.download.answer_key_url,
            },
        }
