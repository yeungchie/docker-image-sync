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


def purge_by_name(name: str) -> None:
    try:
        image = CLIENT.images.get(name)
    except ImageNotFound:
        pass

    containers = getContainers(image)
    if len(containers) > 0:
        container_names = '[+' + ', '.join(str(c.name) for c in containers) + ']'
        print(f'Image "{name}" is being used for container: {container_names}')
        return

    CLIENT.images.remove(name)
    print(f'Image "{image.tags}" is removed')


def purge_none() -> None:
    for image in CLIENT.images.list():
        if not image.tags:
            containers = getContainers(image)
            if len(containers) > 0:
                names = '[+' + ', '.join(str(c.name) for c in containers) + ']'
                print(f'Image "{image.short_id}" is being used for container: {names}')
                continue

            CLIENT.images.remove(image.id, force=True)
            print(f'Image "{image.short_id}" is removed')
