import typing as t
from dataclasses import dataclass
from datetime import datetime

import whoosh.fields


@dataclass
class AuthInfo:
    token: str
    base_url: str


@dataclass
class Bookmark:
    id: str
    url: str
    title: t.Optional[str]
    description: t.Optional[str]
    notes: t.Optional[str]
    web_archive_snapshot_url: t.Optional[str]
    favicon_url: t.Optional[str]
    preview_image_url: t.Optional[str]
    is_archived: t.Optional[bool]
    unread: t.Optional[bool]
    shared: t.Optional[bool]
    tag_names: t.Optional[list[str]]
    date_added: datetime
    date_modified: datetime
    website_title: t.Optional[str]
    website_description: t.Optional[str]
    fulltext: t.Optional[str]


schema = whoosh.fields.Schema(
    id=whoosh.fields.ID(stored=True, unique=True),
    url=whoosh.fields.STORED,
    title=whoosh.fields.TEXT(stored=True),
    description=whoosh.fields.TEXT(stored=True),
    notes=whoosh.fields.TEXT(stored=True),
    web_archive_snapshot_url=whoosh.fields.STORED,
    favicon_url=whoosh.fields.STORED,
    preview_image_url=whoosh.fields.STORED,
    is_archived=whoosh.fields.BOOLEAN(stored=True),
    unread=whoosh.fields.BOOLEAN(stored=True),
    shared=whoosh.fields.BOOLEAN(stored=True),
    tag_names=whoosh.fields.KEYWORD(stored=True),
    date_added=whoosh.fields.DATETIME(stored=True),
    date_modified=whoosh.fields.DATETIME(stored=True),
    website_title=whoosh.fields.TEXT(stored=True),
    website_description=whoosh.fields.TEXT(stored=True),
    fulltext=whoosh.fields.TEXT(stored=True),
)
