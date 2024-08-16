.PHONY:  main clean install uninstall build upload test

main:
	make build

clean:
	make uninstall
	rm -rf docker_image_sync/__pycache__
	rm -rf build
	rm -rf dist
	rm -rf docker_image_sync.egg-info

install:
	pip install .

uninstall:
	pip uninstall docker-image-sync -y

build:
	make clean
	python setup.py sdist build

upload: dist
	python -m twine upload dist/*

test:
	make clean
	python -m docker_image_sync.remote ./config.yaml --try-run
	python -m docker_image_sync.local  ./config.yaml --try-run
