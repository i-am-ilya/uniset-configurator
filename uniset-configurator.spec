Name: uniset-configurator
Version: 0.3
Release: eter2
Summary: UniSet configurator
Group: Development/Python
License: GPL
Url: http://wiki.office.etersoft.ru/asu/Jauza?v=1fw
Source: %name-%version.tar
BuildArch: noarch
# Automatically added by buildreq on Sat Sep 25 2010 (-bi)
BuildRequires: python-devel

%add_findreq_skiplist %_datadir/%name/*.sh

%description
%summary

%prep
%setup

%build
%autoreconf
%configure
%make_build

%install
%make_install install DESTDIR=%buildroot

mkdir %buildroot%python_sitelibdir/%name
mv -f %buildroot%python_sitelibdir/*.py %buildroot%python_sitelibdir/%name/

mkdir %buildroot/%_bindir/
ln -s %python_sitelibdir/%name/%name.py %buildroot/%_bindir/%name
ln -s %python_sitelibdir/%name/io_conf.py %buildroot/%_bindir/uniset-ioconf

%files
%dir %python_sitelibdir/%name
%python_sitelibdir/*
%dir %_datadir/%name/
%_datadir/%name/
%_bindir/*

%changelog
* Wed Oct 20 2010 Pavel Vainerman <pv@altlinux.ru> 0.3-eter2
- fixed bug in previous build

* Wed Oct 20 2010 Pavel Vainerman <pv@altlinux.ru> 0.3-eter1
- add uniset-ioconf utilities
- new version (add new functions)

* Sun Sep 26 2010 Pavel Vainerman <pv@altlinux.ru> 0.2-eter4
- minor fixes

* Sun Sep 26 2010 Pavel Vainerman <pv@altlinux.ru> 0.2-eter3
- minor fixes in card setup dialog

* Sun Sep 26 2010 Pavel Vainerman <pv@altlinux.ru> 0.2-eter2
- add subdev and device file param for card

* Sat Sep 25 2010 Pavel Vainerman <pv@altlinux.ru> 0.1-eter2
- second build

* Sat Sep 25 2010 Pavel Vainerman <pv@altlinux.ru> 0.1-eter1
- initial build
