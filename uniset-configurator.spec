Name: uniset-configurator
Version: 0.1
Release: eter1
Summary: UniSet configurator
Group: Development/Python
License: GPL
Url: http://wiki.office.etersoft.ru/asu/Jauza?v=1fw
Source: %name-%version.tar
BuildArch: noarch
# Automatically added by buildreq on Sat Sep 25 2010 (-bi)
BuildRequires: python-devel

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
#mkdir %buildroot/%_bindir/
#ln -s %python_sitelibdir/%name.py %buildroot/%_bindir/%name.py 

%files
#%dir %python_sitelibdir/%name
%python_sitelibdir/*
%dir %_datadir/%name/
%_datadir/%name/

%changelog
* Sat Sep 25 2010 Pavel Vainerman <pv@altlinux.ru> 0.1-eter1
- initial build

