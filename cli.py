import click
from interface import sync_factory


@click.group()
def cli():
    pass


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument('inputs', nargs=-1)
@click.option('--no-merge', 'merge', is_flag=True, default=True, help='disable merge')
@click.option('--clean-merge', 'rm_existing_tracks', is_flag=True, default=False, help='remove existing tracks')
@click.option('--no-clean', 'delete_mx_source', is_flag=True, default=True, help='disable remove after merge')
@click.option('--force', 'force', is_flag=True, default=False, help='force even though file exists')
def sync(**kwargs):
    sync_factory(**kwargs)


cli = click.CommandCollection(sources=[cli])

if __name__ == '__main__':
    cli()
