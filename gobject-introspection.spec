%define name gobject-introspection
%define version 0.6.3
%define git 0
%if %git
%define release %mkrel 0.%git.1
%else
%define release %mkrel 1
%endif


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
%if %git
Source0:       %{name}-%{git}.tar.bz2
%else
Source0: ftp://ftp.gnome.org/pub/GNOME/sources/%name/%{name}-%{version}.tar.bz2
%endif
Patch1: gobject-introspection-link-module.patch
License: GPLv2+ and LGPLv2+
Group: Development/C
Url: http://www.gnome.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
#gw bootstrap problem, it needs some gir files
BuildRequires: gobject-introspection-devel
BuildRequires: glib2-devel
BuildRequires: ffi5-devel
BuildRequires: python-devel
BuildRequires: freetype2-devel 
BuildRequires: cairo-devel
BuildRequires: fontconfig-devel
BuildRequires: GL-devel
BuildRequires: libxft-devel
BuildRequires: flex bison
BuildRequires: gnome-common
BuildRequires: libtool
BuildRequires: gtk-doc

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
%if %git
%setup -q -n %name
./autogen.sh -V
%else
%setup -q
%endif
%patch1 -p1 -b .link-module

%if %git
./autogen.sh -V
%endif

%build
%define _disable_ld_no_undefined 1
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
%_libdir/%name
%dir %_libdir/girepository-%api
%_libdir/girepository-%api/Everything-1.0.typelib
%_libdir/girepository-%api/GIRepository-2.0.typelib
%_libdir/girepository-%api/GL-1.0.typelib
%_libdir/girepository-%api/GLib-2.0.typelib
%_libdir/girepository-%api/GModule-2.0.typelib
%_libdir/girepository-%api/GObject-2.0.typelib
%_libdir/girepository-%api/Gio-2.0.typelib
%_libdir/girepository-%api/cairo-1.0.typelib
%_libdir/girepository-%api/fontconfig-2.0.typelib
%_libdir/girepository-%api/freetype2-2.0.typelib
%_libdir/girepository-%api/libxml2-2.0.typelib
%_libdir/girepository-%api/xfixes-4.0.typelib
%_libdir/girepository-%api/xft-2.0.typelib
%_libdir/girepository-%api/xlib-2.0.typelib
%dir %_datadir/gir-%api
%_datadir/gir-%api/Everything-1.0.gir
%_datadir/gir-%api/GIRepository-2.0.gir
%_datadir/gir-%api/GL-1.0.gir
%_datadir/gir-%api/GLib-2.0.gir
%_datadir/gir-%api/GModule-2.0.gir
%_datadir/gir-%api/GObject-2.0.gir
%_datadir/gir-%api/Gio-2.0.gir
%_datadir/gir-%api/cairo-1.0.gir
%_datadir/gir-%api/fontconfig-2.0.gir
%_datadir/gir-%api/freetype2-2.0.gir
%_datadir/gir-%api/libxml2-2.0.gir
%_datadir/gir-%api/xfixes-4.0.gir
%_datadir/gir-%api/xft-2.0.gir
%_datadir/gir-%api/xlib-2.0.gir

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
%_datadir/aclocal/*.m4
