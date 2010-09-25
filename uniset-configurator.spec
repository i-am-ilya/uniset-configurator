Name: uniset-configurator
Version: 0.1
Release: eter1
Summary: UniSet configurator
Group: Development/Python
License: GPL
Url: http://wiki.office.etersoft.ru/asu/Jauza?v=1fw
Source: %name-%version.tar
BuildArch: noarch
BuildRequires: rpm-build-compat
Requires: python-module-pisa, python-module-django >= 1.2, python-module-django-dbbackend-mysql, python-module-flup
%description
%summary

%prep
%setup

%install
%make_install install DESTDIR=%buildroot 

%files
%dir %python_sitelibdir/%name


%changelog
