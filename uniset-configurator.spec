Name: uniset-configurator
Version: 0.1
Release: eter1
Summary: UniSet configurator
Group: Development/Python
License: GPL
Url: http://wiki.office.etersoft.ru/asu/Jauza?v=1fw
Source: %name-%version.tar
BuildArch: noarch
# Automatically added by buildreq on Sat Sep 25 2010
BuildRequires: python-base

%description
%summary

%prep
%setup

%build
%autoreconf
%configure
%make_build

%install
%make_install

%files
%dir %python_sitelibdir/%name


%changelog
