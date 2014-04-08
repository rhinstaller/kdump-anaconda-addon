#
# Makefile for the PO files (translation) catalog
#
# $Id: Makefile,v 1.1.1.1 2007/03/08 02:27:37 ccheng Exp $

# What is this package?
NLSPACKAGE	= kdump
POTFILE		= $(NLSPACKAGE).pot
INSTALL		= /usr/bin/install -c
INSTALL_DATA	= $(INSTALL) -m 644
INSTALL_DIR	= /usr/bin/install -d

# destination directory
INSTALL_NLS_DIR = $(DESTDIR)/usr/share/locale

# PO catalog handling
MSGINIT		= msginit --no-translator --input=$(POTFILE)
MSGMERGE	= msgmerge -v --update
XGETTEXT	= xgettext --default-domain=$(NLSPACKAGE) \
		  --add-comments		  
MSGFMT		= msgfmt --statistics --verbose

# What do we need to do
POFILES		= $(wildcard *.po)
MOFILES		= $(patsubst %.po,%.mo,$(POFILES))
PYSRC		= $(wildcard ../*.py)
TUIPYSRC		= $(wildcard ../tui/*.py) $(wildcard ../tui/spokes/*.py)
GUIPYSRC		= $(wildcard ../gui/*.py) $(wildcard ../gui/spokes/*.py)
KSPYSRC		= $(wildcard ../ks/*.py) 
GLADE       = $(wildcard ../gui/spokes/*.glade)
SRCFILES	= $(PYSRC) $(TUIPYSRC) $(GUIPYSRC) $(KSPYSRC) $(GLADE)
LANG		= ar as bg bn_IN bn bs ca cs cy da de el en_GB es et fa fi fr gu he hi hr hu hy id is it ja ka kn ko ku lo lv mk ml mr ms my nb nl or pa pl pt_BR pt ru si sk sl sq sr@Latn sr sv ta_IN ta te tr uk ur vi zh_CN zh_TW
#default:: clean

all:: $(MOFILES)

clean:
	@rm -fv *mo *~ .depend

install: $(MOFILES)
	@for n in $(MOFILES); do \
	    l=`basename $$n .mo`; \
	    $(INSTALL_DIR) $(INSTALL_NLS_DIR)/$$l/LC_MESSAGES; \
	    $(INSTALL_DATA) --verbose $$n $(INSTALL_NLS_DIR)/$$l/LC_MESSAGES/$(NLSPACKAGE).mo; \
	done

%.mo: %.po
	$(MSGFMT) -o $@ $<

$(POTFILE): $(SRCFILES)
	$(XGETTEXT) --output=$(POTFILE) $(SRCFILES)

initpo::$(POTFILE)
	@for lang in $(LANG);do \
	    $(MSGINIT) -l $$lang; \
	done
 
merge: $(POTFILE) $(POFILES)
	for file in $(POFILES); do \
		base=`basename $$file`; \
		echo "$(MSGMERGE) $$base $(NLSPACKAGE).pot"; \
		$(MSGMERGE) $$base $(NLSPACKAGE).pot; \
	done

tgz:
	@rm -rf ../kdump-po
	@mkdir ../kdump-po
	@cp $(POFILES) Makefile ../kdump-po
	@tar -czvf ../kdump-po-$(shell date +%Y%m%d).tgz ../kdump-po

.PHONY: missing depend
