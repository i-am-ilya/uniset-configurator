SUBDIRS = templates cards

bin_SCRIPTS = uniset-io-gentags.sh

python_SCRIPTS 	= uniset_io_conf.py

moddir    = @pythondir@/@PACKAGE@/modules/uniset_io
mod_DATA  = uniset_io.py card_editor.py

ddir     = $(pkgdatadir)
d_DATA   = *.glade *.ui uniset-io-gentags.xsl


uniset-io-gentags.xsl: uniset-io-gentags.xsl.tpl uniset-io-gentags.sh
	$(SHELL) gen-xsltfile.sh $(srcdir)/uniset-io-gentags.xsl.tpl $@
