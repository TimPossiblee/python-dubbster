import os

import FileHandler
import Mixing
from log import log


def sync_factory(**kwargs):
    inputs = kwargs.get('inputs', ())

    if len(inputs) == 1:
        list_sync(inputs[0], **kwargs)
    elif len(inputs) == 2:
        if os.path.isfile(inputs[0]) and os.path.isfile(inputs[1]):
            sync(inputs[0], inputs[1], **kwargs)
        elif os.path.isdir(inputs[0]) and os.path.isdir(inputs[1]):
            directory_sync(inputs[0], inputs[1], **kwargs)


def sync(mx_source: str, adr_source: str, merge=False, delete_mx_source=False, force=False, rm_existing_tracks=False,
         **kwargs):
    mixing = Mixing.Mixing()

    container = Mixing.load_sources(mx_source, adr_source)
    if container is None:
        return mixing

    mixing.frame_path = FileHandler.create_dir(os.path.dirname(__file__), 'tmp')
    mixing.sources = container

    delay = Mixing.mix(mixing)
    if delay is None:
        log.error('delay {} not acceptable'.format(delay))
        return mixing

    if not merge:
        mixing.successful = True
        log.info('not merging success')
        return mixing

    mixing.delay_ms = delay
    mixing.file_out_path = FileHandler.output_filename(container[0].file_name, container[0].file_directory)

    if Mixing.merge(mixing, delete_source=delete_mx_source, remove_multi_track=rm_existing_tracks):
        mixing.successful = True
        log.info('success finished process')
    else:
        log.error('merging was not successful')

    return mixing


def directory_sync(mx_source, adr_source, **kwargs):
    mixing_list = []

    for sources in FileHandler.load_tv(mx_source, adr_source):
        mixing_list.append(sync(sources[0], sources[1], kwargs))

    for mixing in mixing_list:
        if mixing.successful:
            log.info('success {}')
        else:
            log.error('')


def list_sync(source, **kwargs):
    # read txt file and call sync
    print('txt')
