%define name gobject-introspection
%define version 0.9.12
%define git 0
%define rel 1
%if %git
%define release %mkrel -c %git %rel
%else
%define release %mkrel %rel
%endif


%define api 1.0
%define major 1
%define libname %mklibname girepository %api %major
%define develname %mklibname -d girepository

Summary: GObject Introspection
Name: %{name}
Version: %{version}
Release: %{release}
%if %git
Source0:       %{name}-%{git}.tar.xz
%else
Source0: ftp://ftp.gnome.org/pub/GNOME/sources/%name/%{name}-%{version}.tar.bz2
%endif
Patch0: gobject-introspection-fix-link.patch
Patch2: gobject-introspection-add-workarounds-for-libgnomekeyring-and-libgda.patch
License: GPLv2+ and LGPLv2+
Group: Development/C
Url: http://www.gnome.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: glib2-devel >= 2.25.8
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
Conflicts: %{mklibname girepository 1.0 0} < 0.6.10-5mdv
Conflicts: gir-repository < 0.6.5-12.20100622.3mdv

%description
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%package -n %libname
Group: System/Libraries
Summary: GObject Introspection shared library
Conflicts: %name < 0.6.8-2mdv
Requires: %name >= %version

%description -n %libname
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.


%package -n %develname
Group: Development/C
Summary: GObject Introspection development libraries
Requires: %libname = %version-%release
Provides: libgirepository-devel = %version-%release
Provides: %name-devel = %version-%release
#gw /usr/bin/libtool is called in giscanner
Requires: libtool

%description -n %develname
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%prep
%if %git
%setup -q -n %name
%else
%setup -q
%endif
%apply_patches
%if %git
./autogen.sh -V
%else
autoreconf -fi
%endif

%build
%configure2_5x --disable-static --enable-gtk-doc
%make

%install
rm -rf %{buildroot}
%makeinstall_std

%check
#gw: https://bugzilla.gnome.org/show_bug.cgi?id=630136
#make check

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README NEWS TODO AUTHORS
%dir %_libdir/girepository-%api
%_libdir/girepository-%api/DBus-1.0.typelib
%_libdir/girepository-%api/DBusGLib-1.0.typelib
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
%_libdir/girepository-%api/xrandr-1.3.typelib

%files -n %libname
%defattr(-,root,root)
%_libdir/libgirepository-%api.so.%{major}*

%files -n %develname
%defattr(-,root,root)
%doc ChangeLog
%_libdir/libgirepository-%api.so
%_libdir/libgirepository*a
%_libdir/pkgconfig/gobject-introspection-%api.pc
%_libdir/pkgconfig/gobject-introspection-no-export-%api.pc
%_includedir/%name-%api
%_datadir/aclocal/*.m4
%_datadir/%name-%api
%_bindir/g-ir-*
%_libdir/%name
%_datadir/gtk-doc/html/gi
%dir %_datadir/gir-%api
%_datadir/gir-%api/DBus-1.0.gir
%_datadir/gir-%api/DBusGLib-1.0.gir
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
%_datadir/gir-%api/xrandr-1.3.gir
%_mandir/man1/*
