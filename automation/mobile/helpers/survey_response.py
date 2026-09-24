"""The survey a job holds on the server (``GET /job/{id}`` → ``surveyResponse``), read as flat
answers.

Shape (recon 8, 2026-09-24): ``items[]`` in order, each either a loose ``question`` or a ``section``
with ``questions[]``. A repeatable section is saved as one section block per entry, titled
"<section>", "<section> 2", … (D-SRV-14, accepted). A question's answer is ``value[].data``; photos
are ``files[]`` (``note`` = the photo's description, ``location`` = the stored file). Hidden
questions are not saved.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StoredAnswer:
    block: str | None  # the section / entry title; None for a loose question
    title: str
    type: str
    id: str
    values: list = field(default_factory=list)
    files: list[dict] = field(default_factory=list)

    @property
    def notes(self) -> list[str]:
        return [f.get("note") or "" for f in self.files]


def answers(response: dict) -> list[StoredAnswer]:
    """Every saved question, in the saved order."""
    out = []
    for item in response.get("items") or []:
        section = item.get("section")
        questions = section.get("questions") or [] if section else [item.get("question") or {}]
        block = section.get("title") if section else None
        for q in questions:
            out.append(StoredAnswer(
                block, q.get("title", ""), q.get("type", ""), q.get("id", ""),
                [v.get("data") for v in q.get("value") or []], list(q.get("files") or []),
            ))  # fmt: skip
    return out


def blocks(response: dict) -> list[str]:
    """The titles of the saved section blocks, in order (one per entry of a repeatable section)."""
    return [i["section"].get("title", "") for i in response.get("items") or [] if i.get("section")]


def answer(response: dict, title: str, block: str | None = None) -> StoredAnswer:
    """The one saved answer to ``title`` (inside ``block`` when given); raises if it is absent
    or ambiguous."""
    found = [
        a for a in answers(response) if a.title == title and (block is None or a.block == block)
    ]
    if len(found) != 1:
        where = f" in {block!r}" if block else ""
        raise AssertionError(f"{len(found)} saved answers to {title!r}{where}: {found}")
    return found[0]
