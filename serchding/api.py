import typing as t
from datetime import datetime
from urllib.parse import urljoin

import requests
from dacite import from_dict

from .decl import AuthInfo, Bookmark


def api_get_bookmarks(
    authinfo: AuthInfo,
    q: t.Optional[str] = None,
    limit: t.Optional[int] = None,
    offset: t.Optional[int] = None,
) -> dict:
    url = urljoin(authinfo.base_url, "/api/bookmarks")
    params = {"q": q, "limit": limit, "offset": offset}
    headers = {"Authorization": f"Token {authinfo.token}"}
    r = requests.get(url, params=params, headers=headers, timeout=3)
    j = r.json()
    more = j["next"]
    results = j["results"]
    for result in results:
        result["id"] = str(result["id"])
        result["date_added"] = datetime.fromisoformat(result["date_added"])
        result["date_modified"] = datetime.fromisoformat(result["date_modified"])
    bookmarks = [from_dict(Bookmark, result) for result in results]
    summary = {
        "more": more,
        "bookmarks": bookmarks,
    }
    return summary
