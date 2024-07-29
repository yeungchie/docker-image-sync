# Docker Image Sync

## Install

```bash
pip3 install docker_image_sync
```

## Example

+ config.yaml

```yaml
images:
- alpine:latest
- python:latest
- gitlab/gitlab-ce:latest
- homeassistant/home-assistant:latest
registry: my.registry.com
namespace: mynamespace
```

+ try run

```bash
python3 -m docker_image_sync.remote config.yaml --try-run
```

![Demo](https://raw.githubusercontent.com/yeungchie/docker-image-sync/main/img/demo.gif 'Demo')
