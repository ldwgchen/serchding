import click
import whoosh.highlight
import whoosh.qparser
import whoosh.query
import whoosh.searching

from .decl import schema
from .utils import get_index


def search_run(ctx: click.Context, show: bool, query: tuple[str]):
    index = get_index(ctx)
    fields = (
        "title",
        "description",
        "notes",
        "tag_names",
        "fulltext",
    )

    parser = whoosh.qparser.MultifieldParser(
        fields, schema, termclass=whoosh.query.Variations, group=whoosh.qparser.OrGroup
    )
    parser.add_plugin(whoosh.qparser.FuzzyTermPlugin())
    query_str = " ".join(query)
    s = index.searcher()
    q = parser.parse(query_str)
    try:
        results = s.search(q, terms=True)
    except Exception as e:
        s.close()
        ctx.fail(f"Could not search for {q}: {repr(e)}")
    results.fragmenter.charlimit = None
    results.formatter = whoosh.highlight.UppercaseFormatter()
    to_echo = []
    for hit in results:
        stored_fields = hit.fields()
        title = stored_fields.get("title")
        url = stored_fields.get("url")
        to_echo.append(f"--> {title} <{url}>:\n")
        if show:
            fieldnames = set([mt[0] for mt in hit.matched_terms()])
            for fieldname in fieldnames:
                to_echo.append(f'{fieldname}:"{hit.highlights(fieldname)}"\n')
            to_echo.append("\n")
    if show:
        to_echo.pop()
    click.echo("".join(to_echo), nl=False)
    s.close()
