from typing import Optional
import yaml

from docker.errors import ImageNotFound, NotFound

from .image import Image

__all__ = [
    'sync',
]


def sync(
    image_spec: str,
    source_registry: str,
    source_namespace: Optional[str] = None,
    *,
    demo: bool = False,
    richLogHandle=None,
    verbose: bool = False,
):
    # tag
    repo_tag = image_spec.strip().split(':')
    try:
        repo, tag = repo_tag
    except ValueError:
        repo, tag = repo_tag[0], 'latest'

    # domain and image name
    repos = repo.split('/')
    if len(repos) > 1:
        dest_domain = '/'.join(repos[:-1])
        image_name = repos[-1]
    else:
        dest_domain = None
        image_name = repos[0]

    if source_namespace:
        source_domain = f"{source_registry}/{source_namespace}"
    elif dest_domain:
        dest_namespace = dest_domain.split('/')[-1]
        source_domain = f"{source_registry}/{dest_namespace}"
    else:
        source_domain = str(source_registry)

    image = Image(
        source=source_domain,
        dest=dest_domain,
        image=image_name,
        tag=tag,
    )

    image.demo = demo

    if not isinstance(image, Image):
        return ()

    # pull
    try:
        if richLogHandle:
            richLogHandle(
                f'Image Pull >>> {image.source_name}',
                NewLine(1),
            )
        image.pull()
    except ImageNotFound:
        if richLogHandle:
            richLogHandle(f'Image Not Found.', NewLine(1))
        return
    except NotFound:
        if richLogHandle:
            richLogHandle(f'Invalid Tag <{image.tag}>', NewLine(1))
        return

    # tag update
    try:
        if richLogHandle:
            richLogHandle(
                f'Image Tag  >>> {image.source_name} => {image.dest_name}',
                NewLine(1),
            )
        if not image.makeTag():
            if richLogHandle:
                richLogHandle('Image Tag Failed.', NewLine(1))
            return
    except:
        if richLogHandle:
            richLogHandle('Image Tag Failed.', NewLine(1))
        return


if __name__ == '__main__':
    import argparse

    from rich.console import Console, NewLine
    from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
    from rich.rule import Rule

    parse = argparse.ArgumentParser()
    parse.add_argument('config', help='yaml file')
    parse.add_argument('--try-run', action='store_true', help='try run')
    parse.add_argument('--verbose', action='store_true', help='verbose push result')
    args = parse.parse_args()

    if not args.config:
        print('config file is required')
        exit(1)

    with open(args.config, 'r') as f:
        config = yaml.full_load(f)

    registry = config['registry']
    namespace = config.get('namespace', None)

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=Console(log_time_format='[%F %T]'),
        transient=False,
    ) as progress:
        images = config['images']
        task_total = progress.add_task("[red]Image Synchronizing", total=len(images))
        for x in images:
            progress.log(Rule(x.strip()), NewLine(1))
            sync(
                image_spec=x,
                source_registry=registry,
                source_namespace=namespace,
                demo=args.try_run,
                richLogHandle=progress.log,
                verbose=args.verbose,
            )
            progress.log(NewLine(1))
            progress.update(task_total, advance=1)
