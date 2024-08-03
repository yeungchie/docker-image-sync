from typing import Optional, List
import re
import json

import docker
from docker.models.images import Image as DockerImage
from docker.client import DockerClient

__all__ = [
    'Image',
]


class Image:
    '''从 dockerhub 拉取镜像，并推送到私有仓库。

    >>> image = Image(source='gitlab', dest='my_vps/my_namespace', image='gitlab-ce', tag='latest')
    >>> image.pull()
    >>> image.tag()
    >>> image.push()
    '''

    def __init__(
        self,
        *,
        source: Optional[str],
        dest: Optional[str],
        image: str,
        tag: str = 'latest',
    ) -> None:
        self.source_domain = source
        self.dest_domain = dest
        self.image_name = image
        self.tag = tag
        self.demo = False

    @property
    def source_repo(self) -> str:
        if self.source_domain:
            return f'{self.source_domain}/{self.image_name}'
        else:
            return self.image_name

    @property
    def dest_repo(self) -> str:
        if self.dest_domain:
            return f'{self.dest_domain}/{self.image_name}'
        else:
            return self.image_name

    @property
    def source_name(self) -> str:
        return f'{self.source_repo}:{self.tag}'

    @property
    def dest_name(self) -> str:
        return f'{self.dest_repo}:{self.tag}'

    @property
    def _client(self) -> DockerClient:
        if not hasattr(self, '__client'):
            self.__client = docker.from_env()
        return self.__client

    def pull(self) -> Optional[DockerImage]:
        if self._isDemo():
            return
        return self._client.images.pull(self.source_repo, tag=self.tag)

    def get(self) -> Optional[DockerImage]:
        if not self._isDemo():
            return self._client.images.get(self.source_name)

    def makeTag(self) -> Optional[bool]:
        if self._isDemo():
            return True
        image = self.get()
        if isinstance(image, DockerImage):
            return image.tag(self.dest_name)

    def push(self) -> List[dict]:
        if self._isDemo():
            info = '\r\n'.join(
                [
                    f'{{"status": "The push refers to repository [{self.dest_name}]"}}',
                    '{"id": "999999999999", "progressDetail": {}, "status": "Preparing"}',
                    '{"id": "999999999999", "progressDetail": {}, "status": "Waiting"}',
                    '{"id": "999999999999", "progressDetail": {}, "status": "Layer already exists"}',
                    '{"status": "latest: digest: sha256:abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz01 size: 999"}',
                    '{"aux": {"Digest": "sha256:abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz01", "Size": 999, "Tag": "latest"}, "progressDetail": {}}',
                ]
            )
        else:
            info = self._client.images.push(self.dest_repo, tag=self.tag)
        return json.loads('[' + re.sub(r'}\s*{', '},{', info) + ']')

    def _isDemo(self) -> bool:
        if self.demo:
            from time import sleep
            from random import randint

            sleep(randint(0, 10) * 0.1)
            return True
        else:
            return False
