%define name gobject-introspection
%define version 0.6.0
%define release %mkrel 1

%define major 0
%define libname %mklibname girepository %major
%define everythingmajor 1
%define everythinglibname %mklibname girepository-everything %everythingmajor
%define develname %mklibname -d girepository

Summary: GObject Introspection
Name: %{name}
Version: %{version}
Release: %{release}
Source0: http://download.gnome.org/sources/%name/%{name}-%{version}.tar.bz2
License: GPLv2+ and LGPLv2+
Group: Development/C
Url: http://www.gnome.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: glib2-devel
BuildRequires: ffi5-devel
BuildRequires: python-devel
BuildRequires: flex bison
BuildRequires: gnome-common

%description
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%package -n %libname
Group: System/Libraries
Summary: GObject Introspection shared library
%description -n %libname
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%package -n %everythinglibname
Group: System/Libraries
Summary: GObject Introspection shared library
%description -n %everythinglibname
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.


%package -n %develname
Group: Development/C
Summary: GObject Introspection development libraries
Requires: %libname = %version-%release
Requires: %everythinglibname = %version-%release
Requires: %name = %version-%release
Provides: libgirepository-devel = %version-%release
Provides: %name-devel = %version-%release
%description -n %develname
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%prep
%setup -q

%build
%configure2_5x --disable-static
#gw r703 parallel build broken
make

%install
rm -rf %{buildroot}
%makeinstall_std

%clean
rm -rf %{buildroot}

%if %mdvver < 200900
%post -n %libname -p /sbin/ldconfig
%postun -n %libname -p /sbin/ldconfig
%post -n %everythinglibname -p /sbin/ldconfig
%postun -n %everythinglibname -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root)
%doc README NEWS TODO AUTHORS
%_bindir/g-ir-*
%py_platsitedir/giscanner
%_datadir/gir
%_libdir/girepository
%_mandir/man1/*

%files -n %libname
%defattr(-,root,root)
%_libdir/libgirepository.so.%{major}*

%files -n %everythinglibname
%defattr(-,root,root)
%_libdir/libgirepository-everything.so.%{everythingmajor}*

%files -n %develname
%defattr(-,root,root)
%doc ChangeLog
%_libdir/libgirepository.so
%_libdir/libgirepository-everything.so
%_libdir/libgirepository*a
%_libdir/pkgconfig/gobject-introspection-1.0.pc
%_includedir/%name-1.0

