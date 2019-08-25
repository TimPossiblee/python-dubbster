import click
from Hub import Hub


@click.group()
def cli():
    pass


@cli.command()
@click.option('--inputs', '-i', nargs=2, help='enter two inputs for the syncing process')
@click.option('--nomerge', '-nm', is_flag=True, help='set for no auto merging after a successful syncing process')
@click.option('--noclean', '-nc', is_flag=True, help='set for no auto deleting after a successful merging process')
@click.option('--force', '-f', is_flag=True, help='sync even if a multi file exists')
@click.option('--cleanmerge', '-cm', is_flag=True, help='remove synced track in multi file')
@click.option('--batch', '-b', nargs=1, help='enter file for batch syncing')
@click.option('--tv', '-tv', nargs=2, help='enter two inputs for tv syncing process')
def sync(inputs, nomerge, noclean, force, cleanmerge, batch, tv):
    hub = Hub()
    if inputs is not None and len(inputs) != 0:
        hub.cli_sync(sources=inputs, do_merge=not nomerge, delete_source=not noclean,
                     force=force, clean_merge=cleanmerge)
    elif batch is not None and len(batch) != 0:
        hub.cli_sync(file=batch, do_merge=not nomerge, delete_source=not noclean,
                     force=force, clean_merge=cleanmerge)
    elif tv is not None and len(tv) != 0:
        hub.cli_sync(tv=tv, do_merge=not nomerge, delete_source=not noclean,
                     force=force, clean_merge=cleanmerge)


@cli.command()
def batch():
    hub = Hub()
    hub.cli_batch()


cli = click.CommandCollection(sources=[cli])

if __name__ == '__main__':
    cli()
