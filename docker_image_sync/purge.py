from typing import Optional, Union, List

from docker import from_env
from docker.models.images import Image
from docker.models.containers import Container
from docker.errors import ImageNotFound

CLIENT = from_env()


def strfId(id: str) -> str:
    if not id.startswith('sha256:'):
        id = 'sha256:' + id
    if len(id) < 19:
        raise ValueError('Image id is too short - ' + id.ljust(19, '?'))
    return id


def getById(id: str) -> Optional[Image]:
    id = strfId(id)
    image = None
    for i in CLIENT.images.list():
        if isinstance(i.id, str) and i.id.startswith(id):
            image = i
    return image


def getContainers(image_id: Union[str, Image]) -> List[Container]:
    if isinstance(image_id, str):
        image = getById(strfId(image_id))
    else:
        image = image_id
    containers = []
    if image is not None:
        id = image.id
        for c in CLIENT.containers.list():
            if id == c.image.id:
                containers.append(c)
    return containers


def purge_by_name(name: str, logHandle=print) -> None:
    try:
        image = CLIENT.images.get(name)
    except ImageNotFound:
        return

    containers = getContainers(image)
    if len(containers) > 0:
        container_names = '[+' + ', '.join(str(c.name) for c in containers) + ']'
        logHandle(f'Image "{name}" is being used for container: {container_names}')
        return

    CLIENT.images.remove(name)
    logHandle(f'Image "{image.tags}" is removed')


def purge_none(logHandle=print, progress=None) -> None:
    image_list = CLIENT.images.list()
    task = None
    if progress is not None:
        task = progress.add_task("[red]Invalid Image Purge", total=len(image_list))

        def task_update():
            if progress is not None and task is not None:
                progress.update(task, advance=1)

    for image in image_list:
        if not image.tags:
            containers = getContainers(image)
            if len(containers) > 0:
                names = '[+' + ', '.join(str(c.name) for c in containers) + ']'
                logHandle(
                    f'Image "{image.short_id}" is being used for container: {names}'
                )
                task_update()
                continue

            CLIENT.images.remove(image.id, force=True)
            logHandle(f'Image "{image.short_id}" is removed')
        task_update()


if __name__ == '__main__':
    import argparse

    parse = argparse.ArgumentParser()
    parse.add_argument('config', help='yaml file')
    parse.add_argument('--try-run', action='store_true', help='try run')
    args = parse.parse_args()

    if not args.config:
        print('config file is required')
        exit(1)

    import yaml
    from rich.console import Console, NewLine
    from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
    from rich.rule import Rule

    with open(args.config, 'r') as f:
        config = yaml.full_load(f)

    registry = config['registry']
    namespace = config.get('namespace', None)
    images = []

    if namespace is None:
        domain = registry
    else:
        domain = f'{registry}/{namespace}'

    for image in config['images']:
        images.append(f'{domain}/{image}')

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=Console(log_time_format='[%F %T]'),
        transient=False,
    ) as progress:
        progress.log(Rule('[red]Invalid Image Purge'), NewLine(1))
        purge_none(logHandle=progress.log, progress=progress)
        temp_purge_task = progress.add_task(
            '[yellow]Temp Image Purge', total=len(images)
        )
        progress.log(NewLine(1))
        progress.log(Rule('[yellow]Temp Image Purge'), NewLine(1))
        for image in images:
            purge_by_name(image, logHandle=progress.log)
            progress.update(temp_purge_task, advance=1)
