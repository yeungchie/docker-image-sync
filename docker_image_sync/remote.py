import yaml

from docker.errors import ImageNotFound, NotFound

from .image import Image


def sync(image_spec: str, dest_domain: str, *, demo: bool = False, richLogHandle=None):
    # tag
    repo_tag = image_spec.strip().split(':')
    try:
        repo, tag = repo_tag
    except ValueError:
        repo, tag = repo_tag[0], 'latest'

    # domain and image name
    repos = repo.split('/')
    if len(repos) > 1:
        source_domain = '/'.join(repos[:-1])
        image_name = repos[-1]
    else:
        source_domain = None
        image_name = repos[0]

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

    # push
    try:
        if richLogHandle:
            richLogHandle(
                f'Image Push >>> {image.dest_name}',
                NewLine(1),
            )
        res = image.push()
        if richLogHandle:
            richLogHandle(
                Panel(
                    Syntax(
                        yaml.dump(res),
                        lexer='yaml',
                        line_numbers=True,
                        indent_guides=True,
                    ),
                    border_style='blue',
                    title='Push Result',
                    title_align='right',
                    width=None,
                ),
                NewLine(1),
            )
    except:
        if richLogHandle:
            richLogHandle('Image Push Failed.')


if __name__ == '__main__':
    import argparse

    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.console import Console, NewLine
    from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
    from rich.rule import Rule

    parse = argparse.ArgumentParser()
    parse.add_argument('config', help='yaml file')
    parse.add_argument('--try-run', action='store_true', help='try run')
    args = parse.parse_args()

    if not args.config:
        print('config file is required')
        exit(1)

    with open(args.config, 'r') as f:
        config = yaml.full_load(f)

    dest_domain = f"{config['registry']}/{config['namespace']}"
    demo_mode = config.get('demo', False)

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
            sync(x, dest_domain, demo=args.try_run, richLogHandle=progress.log)
            progress.log(NewLine(1))
            progress.update(task_total, advance=1)
