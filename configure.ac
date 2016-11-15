#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

# AC_PREREQ(2.59)
AC_INIT([uniset-configurator], [1.0])
AM_INIT_AUTOMAKE(AC_PACKAGE_NAME,AC_PACKAGE_VERSION)

#AM_GNU_GETTEXT([external])
#AM_GNU_GETTEXT_VERSION(0.13.1)

AC_CONFIG_HEADER(config.h)

dnl Initialize maintainer mode
AM_MAINTAINER_MODE

dnl Checks for programs.
AC_PROG_INSTALL
#AC_PROG_LN_S
#AC_PROG_MAKE_SET

# Checks for libraries.

dnl Python
AM_PATH_PYTHON(,,)
PKG_CHECK_MODULES(PYTHON,python,,exit)

AC_CONFIG_FILES([Makefile
                 uniset-configurator-gentags.sh
                 modules/Makefile
                 modules/can/Makefile
                 modules/can/templates/Makefile
                 modules/uniset_io/Makefile
                 modules/uniset_io/templates/Makefile
                 modules/uniset_io/cards/Makefile
                 modules/uniset_io/uniset-io-gentags.sh
                 modules/nodes/Makefile
                 modules/uniset-comm/Makefile
                 modules/lcaps/Makefile
                 modules/lcaps/templates/Makefile
                 modules/apspanel/Makefile
                 modules/apspanel/templates/Makefile
                 modules/viewer/Makefile
                 modules/unet/Makefile
                 templates/Makefile
                 images/Makefile])
		 
AC_OUTPUT
