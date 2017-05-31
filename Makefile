$(eval NAME := $(shell python setup.py --name))
$(eval PY_NAME := $(shell python setup.py --name | sed 's/-/_/g'))
$(eval VERSION := $(shell python setup.py --version))

SDIST := dist/$(NAME)-$(VERSION).tar.gz
WHEEL := dist/$(PY_NAME)-$(VERSION)-py2.py3-none-any.whl

.PHONY: all
all: build

$(SDIST):
	python setup.py sdist

$(WHEEL):
	python setup.py bdist_wheel

.PHONY: build
build: $(SDIST) $(WHEEL)

.PHONY: install
install: $(WHEEL)
	pip install --user $(WHEEL)

.PHONY: uninstall
uninstall:
	pip uninstall $(NAME)

.PHONY: upload
upload: $(SDIST) $(WHEEL)
	twine upload $(SDIST) $(WHEEL)

.PHONY: clean
clean:
	rm -rf build dist *.egg-info
