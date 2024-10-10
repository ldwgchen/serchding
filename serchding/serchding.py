import click

from .auth import auth_get_run, auth_set_run
from .dump import dump_run
from .search import search_run
from .sync import sync_run
from .utils import validate_base_url, validate_token


@click.group()
def cli():
    """Full-text search for linkding."""
    pass


@cli.group()
def auth():
    """Get or set authorization token or base URL."""
    pass


@auth.command()
def get():
    """Show authorization token and base URL."""
    auth_get_run()


@auth.command()
@click.pass_context
@click.option("--token", "-t", callback=validate_token)
@click.option("--base-url", "-b", callback=validate_base_url)
def set(ctx, token, base_url):
    """Set authorization token or base URL."""
    auth_set_run(ctx, token, base_url)


@cli.command()
@click.pass_context
def sync(ctx):
    """Sync with remote and retrieve fulltexts."""
    sync_run(ctx)


@cli.command(no_args_is_help=True)
@click.pass_context
@click.option("--show/--hide", default=True, show_default=True, help="Show matches.")
@click.argument("query", nargs=-1)
def search(ctx, show, query):
    """Search stored bookmarks."""
    search_run(ctx, show, query)


@cli.command()
@click.pass_context
@click.argument(
    "destdir",
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
)
def dump(ctx, destdir):
    """Dump JSON-formatted stored bookmarks (including retrieved fulltexts) into DESTDIR."""
    dump_run(ctx, destdir)
