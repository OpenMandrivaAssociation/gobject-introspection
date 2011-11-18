%define api 1.0
%define major 1
%define libname %mklibname girepository %{api} %major
%define develname %mklibname -d girepository

Summary: GObject Introspection
Name: gobject-introspection
Version: 1.30.0
Release: 1
License: GPLv2+ and LGPLv2+
Group: Development/C
Url: http://www.gnome.org
Source0: ftp://ftp.gnome.org/pub/GNOME/sources/%{name}/%{name}-%{version}.tar.xz
Patch0: gobject-introspection-fix-link.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gnome-common
BuildRequires:	libtool
BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(cairo-gobject)
BuildRequires:	pkgconfig(gio-2.0)
BuildRequires:	pkgconfig(gio-unix-2.0)
BuildRequires:	pkgconfig(glib-2.0) >= 2.29.7
BuildRequires:	pkgconfig(gmodule-2.0)
BuildRequires:	pkgconfig(gobject-2.0)
BuildRequires:	pkgconfig(gthread-2.0)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	python-devel

#BuildRequires: pkgconfig(freetype2)
#BuildRequires: pkgconfig(fontconfig)
#BuildRequires: pkgconfig(gl)
#BuildRequires: pkgconfig(xft)

Requires: %{libname} = %{version}-%{release}
Conflicts: %{mklibname girepository 1.0 0} < 0.6.10-5
Conflicts: gir-repository < 0.6.5-12.20100622.3

%description
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%package -n %{libname}
Group: System/Libraries
Summary: GObject Introspection shared library
Conflicts: %{name} < 0.6.8-2

%description -n %{libname}
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%package -n %{develname}
Group: Development/C
Summary: GObject Introspection development libraries
Requires: %{libname} = %{version}-%{release}
#gw /usr/bin/libtool is called in giscanner
Requires: libtool
Provides: libgirepository-devel = %{version}-%{release}
Provides: %{name}-devel = %{version}-%{release}

%description -n %{develname}
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%prep
%setup -q
%apply_patches

%build
%configure2_5x \
	--disable-static

%make

%install
rm -rf %{buildroot}
%makeinstall_std

find %{buildroot} -name '*.la' -exec rm -f {} \;

%check
make check

%define typelibs DBus-1.0 DBusGLib-1.0 GIRepository-2.0 GL-1.0 GLib-2.0 \
GModule-1.0 GObject-2.0 Gio-2.0 cairo-1.0 fontconfig-2.0 freetype2-2.0 \
libxml2-2.0 xfixes-4.0 xft-2.0 xlib-2.0 xrandr-1.3

%files
%doc README
%dir %{_libdir}/girepository-%{api}
%(for typelib in %{typelibs}; do
	echo "%{_libdir}/girepository-%{api}/$typelib.typelib"
done)

%files -n %{libname}
%{_libdir}/libgirepository-%{api}.so.%{major}*

%files -n %{develname}
%doc ChangeLog TODO NEWS AUTHORS
%{_bindir}/g-ir-*
%{_libdir}/%{name}
%{_libdir}/libgirepository-%{api}.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/%{name}-%{api}
%{_datadir}/aclocal/*.m4
%{_datadir}/%{name}-%{api}
%{_datadir}/gtk-doc/html/gi
%dir %{_datadir}/gir-%{api}
%(for typelib in %{typelibs}; do
	echo "%{_datadir}/gir-%{api}/$typelib.gir"
done)
%{_mandir}/man1/*
