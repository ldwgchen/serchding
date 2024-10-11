from cleantext import clean

import re
import typing as t
from functools import partial, wraps
from pathlib import Path

import click
import html2text
import requests
import whoosh.fields
import whoosh.index
import whoosh.qparser
import whoosh.searching
from validators.url import url
from fake_useragent import UserAgent

from .decl import AuthInfo, schema

app_dir = Path(click.get_app_dir("serchding"))
token_path = app_dir / "token"
base_url_path = app_dir / "base_url"
index_dir = app_dir / "index"

type _RequireContextCallable[**P] = t.Callable[t.Concatenate[click.Context, P], t.Any]

html2text.hn = lambda _: 0
_h = html2text.HTML2Text()
_h.images_to_alt = True
_h.single_line_break = True
_h.ignore_emphasis = True
_h.ignore_links = True
_h.ignore_tables = True


def ensure_dir(
    dir: Path,
) -> t.Callable[[_RequireContextCallable], _RequireContextCallable]:
    def decorator(f) -> _RequireContextCallable:
        @wraps(f)
        def wrapper(ctx: click.Context, *args, **kwargs):
            if not dir.is_dir():
                try:
                    dir.mkdir(parents=True)
                except Exception as e:
                    ctx.fail(f"Could not make directory at {dir}: {repr(e)}")
            return f(ctx, *args, **kwargs)

        return wrapper

    return decorator


def _get_auth(*, entry_name: t.Literal["token", "base_url"]) -> str:
    match entry_name:
        case "token":
            entry_path = token_path
        case "base_url":
            entry_path = base_url_path

    entry = entry_path.read_text()
    entry = re.search(r"\S*", entry).group()
    return entry


get_token: t.Callable[[], str] = partial(_get_auth, entry_name="token")
get_base_url: t.Callable[[], str] = partial(_get_auth, entry_name="base_url")


def get_authinfo(ctx: click.Context) -> AuthInfo:
    try:
        token = get_token()
    except Exception as e:
        ctx.fail(f"Could not read token: {repr(e)}")
    try:
        base_url = get_base_url()
    except Exception as e:
        ctx.fail(f"Could not read base_url: {repr(e)}")
    return AuthInfo(token=token, base_url=base_url)


@ensure_dir(app_dir)
def _set_auth(
    ctx: click.Context, value: str, *, entry_name: t.Literal["token", "base_url"]
):
    match entry_name:
        case "token":
            entry_path = token_path
        case "base_url":
            entry_path = base_url_path

    try:
        entry_path.write_text(value + "\n")
    except Exception as e:
        ctx.fail(f"Could not write to {entry_path}: {repr(e)}")


set_token: t.Callable[[click.Context, str], None] = partial(
    _set_auth, entry_name="token"
)
set_base_url: t.Callable[[click.Context, str], None] = partial(
    _set_auth, entry_name="base_url"
)


def validate_token(ctx, param, value):
    if not value:
        return
    input_length = len(value)
    if not input_length == 40 or not re.fullmatch(r"\w*", value, re.ASCII):
        raise click.BadParameter(f"'{value}' is not a token")
    return value


def validate_base_url(ctx, param, value):
    if not value:
        return
    if not url(value):
        raise click.BadParameter(f"'{value}' is not a valid url")
    return value


def get_fulltext_from_url(url: str) -> str:
    r = requests.get(url, timeout=2, headers={"user-agent": UserAgent().random})
    r.raise_for_status()
    fulltext = _h.handle(r.text)
    fulltext = clean(
        fulltext,
        no_line_breaks=True,
        no_urls=True,
        no_punct=True,
        no_emoji=True,
    )
    return fulltext


@ensure_dir(index_dir)
def get_index(ctx: click.Context) -> whoosh.index.Index:
    if whoosh.index.exists_in(index_dir):
        try:
            index = whoosh.index.open_dir(index_dir)
        except Exception as e:
            ctx.fail(f"Could not open index at {index_dir}: {repr(e)}")
    else:
        try:
            index = whoosh.index.create_in(index_dir, schema)
        except Exception as e:
            ctx.fail(f"Could not create index at {index_dir}: {repr(e)}")
    return index
