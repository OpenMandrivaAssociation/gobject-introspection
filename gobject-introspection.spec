%define name gobject-introspection
%define version 0.6.2
%define release %mkrel 1

%define api 1.0
%define major 0
%define libname %mklibname girepository %api %major
%define everythingmajor 1
%define everythinglibname %mklibname girepository-everything %api %everythingmajor
%define develname %mklibname -d girepository

Summary: GObject Introspection
Name: %{name}
Version: %{version}
Release: %{release}
Source0: ftp://ftp.gnome.org/pub/GNOME/sources/%name/%{name}-%{version}.tar.bz2
Patch0: gobject-introspection-0.6.1-fix-str-fmt.patch
Patch1: gobject-introspection-0.6.1-link-module.patch
License: GPLv2+ and LGPLv2+
Group: Development/C
Url: http://www.gnome.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: glib2-devel
BuildRequires: ffi5-devel
BuildRequires: python-devel
BuildRequires: freetype2-devel cairo-devel fontconfig-devel
BuildRequires: flex bison
BuildRequires: gnome-common
BuildRequires: libtool

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
%patch0 -p0
%patch1 -p0

%build
%configure2_5x --disable-static
%make

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
%_libdir/girepository-%api
%_datadir/gir-%api
%_mandir/man1/*

%files -n %libname
%defattr(-,root,root)
%_libdir/libgirepository-%api.so.%{major}*

%files -n %everythinglibname
%defattr(-,root,root)
%_libdir/libgirepository-everything-%api.so.%{everythingmajor}*

%files -n %develname
%defattr(-,root,root)
%doc ChangeLog
%_libdir/libgirepository-%api.so
%_libdir/libgirepository-everything-%api.so
%_libdir/libgirepository*a
%_libdir/pkgconfig/gobject-introspection-%api.pc
%_includedir/%name-%api

