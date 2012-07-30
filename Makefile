SHELL=/usr/bin/env bash
.PHONY: start stop deploy clean test

log:
	mkdir log

virtual_env:
	@virtualenv --no-site-packages --python=python2.7 virtual_env
	@source virtual_env/bin/activate && pip install -r freezer.pip

start: virtual_env log
	@source virtual_env/bin/activate && supervisord --configuration supervisord.conf

debug: virtual_env
	@source virtual_env/bin/activate && ./server.py start

stop:
	@for pid in `ps -ef | grep '$(CURDIR)/server.py' | grep -v grep | awk '{ print($$2) }'`; do kill $$pid; done

deploy:
	fab deploy:name=uploader --host ${HOST}

deploy_vagrant:
	fab vagrant_deploy:name=uploader

test: virtual_env
	source virtual_env/bin/activate && ./server.py test

clean:
	@rm -rf virtual_env
	@rm -rf log/*
