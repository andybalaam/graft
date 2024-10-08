all: test

setup:
	sudo apt install \
		libgtk-3-dev\
		python3 \
		python3-attr \
		python3-gi \
		python3-gi-cairo \
		python3-pytest \
		python3-pytest-pep8 \
		python3-pytest-pylint \
		pylama \
		libgtk-3-dev \


test:
	pytest-3 --pep8 -vv


test-full:
	pytest-3 \
		--quiet \
		--pep8 \
		--pylama \
		--pylint --pylint-rcfile=.pylintrc \

docker-build:
	docker build -t graft .
