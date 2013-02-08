SHELL=/bin/bash
with_brew=bash -i -c 'source ~/.pythonbrew/etc/bashrc && $(1)'
with_venv=bash -i -c 'source ~/.pythonbrew/etc/bashrc && pythonbrew venv use .pyenv && $(1)'

.PHONY: clean start test debug setup freeze docs show_config git_hooks crontab

$(if $(shell test -f ~/.pythonbrew/etc/bashrc && echo pants;  ), $(info found me some brew), $(error OH SHIT, NO BREW))
debug: .pyenv
	@exec $(call with_venv, exec pyserver/bin/server debug)

.pyenv:
	$(call with_brew, pythonbrew venv create --no-site-packages .pyenv)
	$(call with_venv, pip install -r pyserver/etc/frozen)
	-mkdir tmp
	$(call with_venv, cd tmp/ && curl -O http://public.intimidatingbits.com/pypackages/birkenfeld-sphinx-contrib-f60d4a35adab.tar.gz)
	$(call with_venv, cd tmp/ && tar zxf birkenfeld-sphinx-contrib-f60d4a35adab.tar.gz)
	$(call with_venv, cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py build)
	$(call with_venv, cd tmp/birkenfeld-sphinx-contrib-f60d4a35adab/httpdomain && python setup.py install)
	cd tmp/ && curl -O http://public.intimidatingbits.com/apsw-3.7.14.1-r1.zip
	cd tmp/ && unzip apsw-3.7.14.1-r1.zip
	$(call with_venv, cd tmp/apsw-3.7.14.1-r1 && python setup.py fetch --all --missing-checksum-ok build --enable-all-extensions install)
	-rm -rf tmp/
	touch .pyenv

var/logs: 
	mkdir -p var/logs

.doc_build:
	mkdir -p .doc_build/text
	mkdir -p .doc_build/doctrees

setup: var/logs
	
start: setup .pyenv
	@exec $(call with_venv, exec pyserver/bin/server start)

test: .pyenv
	@-rm -rf ./output
	@-find . -name '*.pyc' | xargs rm
ifdef TESTS
	@$(call with_venv, export ROOT_STORAGE_PATH=./output && nosetests -v -s --tests ${TESTS})
else
	@$(call with_venv, export ROOT_STORAGE_PATH=./output && nosetests -v -s)
endif

show_config:
	@pyserver/bin/server config

freeze: .pyenv
	$(call with_venv, pip freeze)

docs: .doc_build .pyenv
	rm -rf .doc_build/text/*
	rm -rf .doc_build/doctrees/*
	$(call with_venv, sphinx-build -n -b text -d .doc_build/doctrees documentation .doc_build/text)
	cp .doc_build/text/index.txt README

clean: setup
	- @rm -rf var/
	- @rm -rf tmp/
	- @rm .pyenv
	@ $(call with_brew, pythonbrew venv delete .pyenv)

git_hooks:
	@cp pyserver/etc/git_hooks/* .git/hooks

crontab:
	@if [ -f ./crontab ]; then cat ./crontab | crontab; fi

# allows for projects using this framework to extend the Makefile
-include Makefile.child

