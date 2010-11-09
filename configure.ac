#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

# AC_PREREQ(2.59)
AC_INIT([uniset-configurator], [0.5])
AM_INIT_AUTOMAKE(AC_PACKAGE_NAME,AC_PACKAGE_VERSION)

#AM_GNU_GETTEXT([external])
#AM_GNU_GETTEXT_VERSION(0.13.1)

AC_CONFIG_HEADER(config.h)

dnl Initialize maintainer mode
AM_MAINTAINER_MODE

dnl Checks for programs.
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_MAKE_SET

# Checks for libraries.

dnl Python
AM_PATH_PYTHON(2.6)
#AM_CHECK_PYTHON_HEADERS(,[AC_MSG_ERROR([python headers not found]);exit] )

AC_CONFIG_FILES([Makefile
                 modules/Makefile
                 modules/can/Makefile
                 modules/can/templates/Makefile
                 modules/uniset_io/Makefile
                 modules/uniset_io/templates/Makefile
                 modules/nodes/Makefile
                 modules/uniset/Makefile
                 modules/lcaps/Makefile
                 modules/lcaps/templates/Makefile
                 modules/apspanel/Makefile
                 modules/apspanel/templates/Makefile
                 templates/Makefile])
		 
AC_OUTPUT
