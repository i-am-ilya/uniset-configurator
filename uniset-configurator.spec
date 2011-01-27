Name: uniset-configurator
Version: 0.6
Release: alt15
Summary: UniSet configurator
Group: Development/Python
License: GPL
Url: http://wiki.office.etersoft.ru/asu/Jauza?v=1fw

Packager: Pavel Vainerman <pv@altlinux.ru>

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

mkdir -p %buildroot%python_sitelibdir/%name
mv -f %buildroot%python_sitelibdir/*.py %buildroot%python_sitelibdir/%name/

mkdir -p %buildroot/%_bindir/
ln -s %python_sitelibdir/%name/%name.py %buildroot/%_bindir/%name
ln -s %python_sitelibdir/%name/uniset_io_conf.py %buildroot/%_bindir/uniset-ioconf
ln -s %python_sitelibdir/%name/lcaps_conf.py %buildroot/%_bindir/uniset-lcaps-conf
ln -s %python_sitelibdir/%name/apspanel_conf.py %buildroot/%_bindir/uniset-apspanel-conf
ln -s %python_sitelibdir/%name/can_conf.py %buildroot/%_bindir/uniset-can-conf

%files
%dir %python_sitelibdir/%name
%python_sitelibdir/*
%dir %_datadir/%name/
%_datadir/%name/
%_datadir/%name/templates
%_bindir/*

%changelog
* Mon Jan 17 2011 Ilya Shpigor <elly@altlinux.org> 0.6-alt14
- fix build for x86_64 arch

* Mon Jan 17 2011 Ilya Shpigor <elly@altlinux.org> 0.6-alt13
- initial build for ALT Linux Sisyphus

* Fri Jan 14 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-eter12
- fixed bug in io-conf (change card number for sensors)

* Wed Jan 12 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-eter11
- fixed bug in io-conf (number of channels for DO32 and DI32)

* Tue Jan 11 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-eter10
- fixed bug (add new sensor)

* Wed Dec 08 2010 Pavel Vainerman <pv@altlinux.ru> 0.6-eter9
- fixed bug in i/o (thank's yv@ again)

* Wed Dec 08 2010 Pavel Vainerman <pv@altlinux.ru> 0.6-eter8
- fixed bug (thank`s yv@)

* Thu Nov 18 2010 Ilya Shpigor <elly@altlinux.org> 0.6-eter7
- fix python version requires in configure.ac

* Tue Nov 09 2010 Pavel Vainerman <pv@altlinux.ru> 0.6-eter3
- minor fixes in io_conf and can_conf

* Tue Nov 09 2010 Pavel Vainerman <pv@altlinux.ru> 0.6-eter2
- add to CANEditor: card parameters editor

* Sun Nov 07 2010 Pavel Vainerman <pv@altlinux.ru> 0.6-eter1
- add apspanel editor

* Fri Nov 05 2010 Pavel Vainerman <pv@altlinux.ru> 0.5-eter6
- rebuild new verion

* Fri Nov 05 2010 Pavel Vainerman <pv@altlinux.ru> 0.5-eter5
- set executable bit for lcaps-conf and uniset-ioconf

* Fri Nov 05 2010 Pavel Vainerman <pv@altlinux.ru> 0.5-eter4
- add 'ALL' for lcaps-conf --gen-test-skel

* Fri Nov 05 2010 Pavel Vainerman <pv@altlinux.ru> 0.4-eter3
- new release (master merge aps)

* Fri Nov 05 2010 Pavel Vainerman <pv@altlinux.ru> 0.4-eter2
- add link for uniset-lcaps-conf

* Fri Nov 05 2010 Pavel Vainerman <pv@altlinux.ru> 0.4-eter1
- add LCAPS test generator 

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
