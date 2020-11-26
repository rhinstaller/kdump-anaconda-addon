-include version.sh

NAME = kdump-anaconda-addon

VERSION = $(shell [ -d .git ] && git describe --tags 2>/dev/null || echo $(KDUMP_ADDON_VERSION))
ADDON = com_redhat_kdump
TESTS = test

FILES = $(ADDON) \
	po \
	Makefile \
	README \
	kdump.svg \
	data/*.service \
	data/*.conf \
	version.sh

EXCLUDES = \
	*~ \
	*.pyc

all:
	@echo "usage: make dist"
	@echo "       make test"
	@echo "       make install"
	@echo "       make uninstall"
	@echo "       make container-test"

DISTNAME = $(NAME)-$(VERSION)
ADDONDIR = /usr/share/anaconda/addons/
SERVICEDIR = /usr/share/anaconda/dbus/services/
CONFDIR = /usr/share/anaconda/dbus/confs/
DISTBALL = $(DISTNAME).tar.gz
NUM_PROCS = $$(getconf _NPROCESSORS_ONLN)
ICONDIR = /usr/share/icons/hicolor/scalable/apps/
CONTAINER_NAME = kdump-anaconda-addon-ci

install: version.sh
	mkdir -p $(DESTDIR)$(ADDONDIR)
	mkdir -p $(DESTDIR)$(ICONDIR)
	cp -rv $(ADDON) $(DESTDIR)$(ADDONDIR)
	install -c -m 644 kdump.svg $(DESTDIR)$(ICONDIR)
	install -c -m 644 data/*.service $(DESTDIR)$(SERVICEDIR)
	install -c -m 644 data/*.conf $(DESTDIR)$(CONFDIR)
	$(MAKE) install-po-files

uninstall:
	rm -rfv $(DESTDIR)$(ADDONDIR)

dist: version.sh
	rm -rf $(NAME)
	mkdir -p $(NAME)
	@if test -d ".git"; \
	then \
		echo Creating ChangeLog && \
		( cd "$(top_srcdir)" && \
		  echo '# Generate automatically. Do not edit.'; echo; \
		  git log --stat --date=short ) > ChangeLog.tmp \
		&& mv -f ChangeLog.tmp $(NAME)/ChangeLog \
		|| ( rm -f ChangeLog.tmp ; \
		     echo Failed to generate ChangeLog >&2 ); \
	else \
		echo A git clone is required to generate a ChangeLog >&2; \
	fi
	for file in $(FILES); do \
		cp -rpv $$file $(NAME)/$$file; \
	done
	for excl in $(EXCLUDES); do \
		find $(NAME) -name "$$excl" -delete; \
	done
	tar -czvf $(DISTBALL) $(NAME)
	rm -rf $(NAME)

potfile:
	$(MAKE) DESTDIR=$(DESTDIR) -C po potfile

po-pull:
	tx pull -a --disable-overwrite

install-po-files:
	$(MAKE) -C po install

container-test:
	podman build --tag $(CONTAINER_NAME) --file test/Dockerfile
	podman run --volume .:/kdump-anaconda-addon:Z $(CONTAINER_NAME) make test

test: runpylint unittest

runpylint:
	@echo "***Running pylint checks***"
	pylint com_redhat_kdump -E 2> /dev/null
	@echo "[ OK ]"

unittest:
	@echo "***Running unittests checks***"
	PYTHONPATH=. python3 -m nose --processes=-1 -vw test/unittests

version.sh:
	@echo "KDUMP_ADDON_VERSION=$(VERSION)" > version.sh

clean:
	$(MAKE) clean -C po
	rm -f *.gz
	rm -f version.sh
	rm -f test/updates.img

.PHONY: install clean container-test test runpylint unittest all version.sh
