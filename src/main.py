import click

from source.la.treebank.source import TreebankSource
from source.source import SourceCode
from strings import code_string


@click.command(name="source")
@click.option(
    "--source",
    "-s",
    required=True,
    type=click.Choice([c.value for c in SourceCode]),
    help="The source to download",
)
@click.option(
    "--count",
    "-c",
    is_flag=True,
    help="Displays the count of data source items",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Forces downloading and persisting of the source"
    + "even if this happened already",
)
def source(source, count, force):
    source_instance = None
    if source == SourceCode.TREEBANK.value:
        source_instance = TreebankSource()

    if not source_instance:
        click.echo(f"The source '{source}' has not yet been implemented")
        return

    click.echo(f"\nDownloading and persisting data for source {source}...\n")
    store_codes = source_instance.store(force)

    for code in store_codes:
        click.echo(code_string(code, source))

    if count:
        click.echo(
            f"The source '{source}' "
            + f"contains {source_instance.count()} elements"
        )


@click.group()
def perlego():
    pass


perlego.add_command(source)

if __name__ == "__main__":
    perlego()
