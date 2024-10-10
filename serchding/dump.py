import json
import re
from pathlib import Path

import click

from .utils import get_index


def dump_run(ctx: click.Context, destdir: str):
    re.compile(r"\d*", re.ASCII)
    dst_dir = Path(destdir)
    ix = get_index(ctx)

    try:
        r = ix.reader()
        stored = [sf for sf in r.all_stored_fields()]
        r.close()
    except Exception as e:
        ctx.fail(f"An exception occurred while reading stored bookmarks: {repr(e)}")

    for sf in stored:
        sf["date_added"] = sf["date_added"].isoformat()
        sf["date_modified"] = sf["date_modified"].isoformat()
        id = sf["id"]
        if not re.fullmatch(r"\d*", id, re.ASCII):
            ctx.fail(f"Found invalid id: {id}")
        file_path = dst_dir / f"{id}.json"
        try:
            f = open(file_path, "w")
            json.dump(sf, f, indent=4)
        except Exception as e:
            f.close()
            ctx.fail(f"Could not dump json to {file_path}: {repr(e)}")
        else:
            f.close()
