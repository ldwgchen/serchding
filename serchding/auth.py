import typing as t

import click

from .utils import get_base_url, get_token, set_base_url, set_token


def auth_get_run():
    try:
        token = get_token()
    except Exception:
        token = ""
    try:
        base_url = get_base_url()
    except Exception:
        base_url = ""
    click.echo(f"token: {token}\nbase_url: {base_url}")


def auth_set_run(ctx: click.Context, token: t.Optional[str], base_url: t.Optional[str]):
    if token:
        set_token(ctx, token)
    if base_url:
        set_base_url(ctx, base_url)
