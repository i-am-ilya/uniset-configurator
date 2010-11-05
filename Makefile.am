SUBDIRS = modules templates

pyexec_SCRIPTS 	= *.py

confdir     = $(pkgdatadir)
conf_DATA   = *.glade

#if MAINTAINER_MODE
#MAINTAINER=locale/lstart.mo
#else
#MAINTAINER=
#endif

#all: configure-text.py $(MAINTAINER)
#	

#configure-text.py: $(top_srcdir)/conf/configure.xml $(top_srcdir)/Utilities/xslt/py-configure.xsl
#	( cd $(top_builddir)/Utilities/xslt/; sh ./mk-py-conf.sh ) > $@

#locale/uniset-configurator.mo:
#	( cd $(top_srcdir)/po ; make install-data-yes localedir=../src/pyGUI/locale )
