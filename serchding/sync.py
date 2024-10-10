from dataclasses import asdict

import click
import whoosh.writing
from dacite import from_dict

from .api import api_get_bookmarks
from .decl import AuthInfo, Bookmark
from .utils import (
    get_authinfo,
    get_fulltext_from_url,
    get_index,
)


def _pull_bookmarks(ctx: click.Context, authinfo: AuthInfo) -> list[Bookmark]:
    offset = 0
    more = True
    bookmarks = []
    while more:
        try:
            rv = api_get_bookmarks(authinfo, offset=offset)
            bookmarks.extend(rv["bookmarks"])
            more = rv["more"]
        except Exception as e:
            ctx.fail(f"Failed to get bookmarks: {repr(e)}")
        else:
            offset += 100
    click.echo(f"Pulled {len(bookmarks)} bookmarks")
    return bookmarks


def sync_run(ctx: click.Context):
    authinfo = get_authinfo(ctx)
    bookmarks = _pull_bookmarks(ctx, authinfo)
    ix = get_index(ctx)

    stored_bookmarks = []
    try:
        r = ix.reader()
        for sf in r.all_stored_fields():
            stored_bookmarks.append(from_dict(Bookmark, sf))
        r.close()
    except Exception as e:
        ctx.fail(f"An exception occurred while reading stored bookmarks: {repr(e)}")

    reusable_fulltexts = {
        sbm.url: sbm.fulltext for sbm in stored_bookmarks if sbm.fulltext
    }

    with click.progressbar(bookmarks, label="Getting fulltexts") as bar:
        for bm in bar:
            if bm.url in reusable_fulltexts:
                bm.fulltext = reusable_fulltexts[bm.url]
            else:
                try:
                    bm.fulltext = get_fulltext_from_url(bm.url)
                except Exception as e:
                    click.echo(
                        f"Could not get fulltext from {bm.url}: {repr(e)}",
                        err=True,
                    )

    try:
        w = ix.writer()
        for bm in bookmarks:
            w.add_document(**asdict(bm))
        w.commit(mergetype=whoosh.writing.CLEAR)
    except Exception as e:
        ctx.fail(f"An exception occurred while writing bookmarks to index: {repr(e)}")
    else:
        click.echo("Saved bookmarks")
