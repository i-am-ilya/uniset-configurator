Name: uniset-configurator
Version: 0.9
Release: alt3
Summary: UniSet configurator
Group: Development/Python
License: GPL
Url: http://wiki.office.etersoft.ru/asu/Jauza?v=1fw

Packager: Pavel Vainerman <pv@altlinux.ru>

Source: %name-%version.tar
BuildArch: noarch

# Automatically added by buildreq on Sat Sep 25 2010 (-bi)
BuildRequires: python-devel
BuildRequires(pre): rpm-build-python

%add_findreq_skiplist %_datadir/%name/*.sh
%global _target_python_libdir %_target_libdir_noarch
%define python_sitelibdir_noarch %python_sitelibdir
%define python_sitelibdir_arch %_libdir/python%__python_version/site-packages

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

if [ %python_sitelibdir_arch != %python_sitelibdir_noarch -a -d %buildroot%python_sitelibdir_arch/%name ]; then
    mkdir -p %buildroot%python_sitelibdir_noarch
    mv %buildroot%python_sitelibdir_arch/%name %buildroot%python_sitelibdir_noarch/
    mv %buildroot%python_sitelibdir_arch/*.py %buildroot%python_sitelibdir_noarch/
fi
mkdir -p %buildroot%python_sitelibdir_noarch/%name
mv -f %buildroot%python_sitelibdir_noarch/*.py %buildroot%python_sitelibdir_noarch/%name/

mkdir -p %buildroot/%_bindir/
ln -s %python_sitelibdir_noarch/%name/%name.py %buildroot/%_bindir/%name
ln -s %python_sitelibdir_noarch/%name/uniset_io_conf.py %buildroot/%_bindir/uniset-ioconf
ln -s %python_sitelibdir_noarch/%name/lcaps_conf.py %buildroot/%_bindir/uniset-lcaps-conf
ln -s %python_sitelibdir_noarch/%name/apspanel_conf.py %buildroot/%_bindir/uniset-apspanel-conf
ln -s %python_sitelibdir_noarch/%name/can_conf.py %buildroot/%_bindir/uniset-can-conf

%files
%dir %python_sitelibdir/%name
%python_sitelibdir/*
%dir %_datadir/%name/
%_datadir/%name/
%_datadir/%name/templates
%_datadir/%name/images
%_bindir/*

%changelog
* Tue Oct 04 2011 Pavel Vainerman <pv@altlinux.ru> 0.9-alt3
- add "unet" configurator

* Sun Jul 24 2011 Pavel Vainerman <pv@altlinux.ru> 0.8-alt8
- fixed bug in io-modules (processing threshold_aid)

* Tue Jun 21 2011 Pavel Vainerman <pv@altlinux.ru> 0.8-alt7
- fixed minor bug in io-module

* Fri May 20 2011 Pavel Vainerman <pv@altlinux.ru> 0.8-alt6
- (can-editor): fixed bug in can200mp config dialog

* Tue May 17 2011 Pavel Vainerman <pv@altlinux.ru> 0.8-alt5
- minor fixes in can.glade

* Tue May 17 2011 Pavel Vainerman <pv@altlinux.ru> 0.8-alt4
- minor fixed in glade-files (spinbutton problem)

* Sat Apr 23 2011 Pavel Vainerman <pv@altlinux.ru> 0.8-alt2
- remove the packing of unnecessary glade-files

* Fri Apr 22 2011 Evgeny Sinelnikov <sin@altlinux.ru> 0.8-alt1
- Strip common glade-file on separate glade-files for every module

* Fri Apr 22 2011 Pavel Vainerman <pv@altlinux.ru> 0.7-alt5
- minor fixes in lcaps editor

* Thu Apr 21 2011 Pavel Vainerman <pv@altlinux.ru> 0.7-alt4
- fixed minor bug in apspanel editor

* Mon Apr 18 2011 Pavel Vainerman <pv@altlinux.ru> 0.7-alt3
- (ioconf): change io="nodeID" to io="nodeName"

* Mon Apr 11 2011 Pavel Vainerman <pv@altlinux.ru> 0.7-alt2
- decrease dependence on python

* Sun Mar 27 2011 Pavel Vainerman <pv@altlinux.ru> 0.7-alt1
- add new card type (AIxxx/8 and AIxx/16)

* Sat Mar 26 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-alt23
- fixed bug in subdev number for ai16, ao16 cards

* Wed Mar 23 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-alt22
- add popupmenu for io channel
- minor fixes

* Sat Mar 19 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-alt21
- add pictures for can-editor

* Fri Mar 18 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-alt20
- add pictures for node-editor and  io-editor

* Fri Mar 18 2011 Pavel Vainerman <pv@server> 0.6-alt19
- add 'hack' for run with new python

* Tue Feb 01 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-alt18
- fixed bug in apspanel module

* Mon Jan 31 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-alt17
- fixed bug in apspanel module (don`t save comment)

* Fri Jan 28 2011 Pavel Vainerman <pv@altlinux.ru> 0.6-alt16
- add generic 'dev' for ioconf 

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
