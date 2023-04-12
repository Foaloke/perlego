import click

from commands.source.la.trascrizioni.source import TrascrizioniSource
from commands.source.la.treebank.source import TreebankSource
from commands.source.source import SourceCode
from strings import code_string


def source_command(source, count, force):
    source_instance = None
    if source == SourceCode.TREEBANK.value:
        source_instance = TreebankSource()
    if source == SourceCode.TRASCRIZIONI.value:
        source_instance = TrascrizioniSource()

    if not source_instance:
        click.echo(f"The source '{source}' has not yet been implemented")
        return

    if count:
        click.echo(
            f"The source '{source}' "
            + f"contains {source_instance.count()} elements"
        )
        return

    click.echo(f"\nDownloading and persisting data for source {source}...\n")
    store_codes = source_instance.store(force)

    for code in store_codes:
        click.echo(code_string(code, source))
