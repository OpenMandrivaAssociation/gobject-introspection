%define build_bootstrap	0
%define api 1.0
%define major 1
%define libname %mklibname girepository %{api} %{major}
%define develname %mklibname -d girepository

Summary:	GObject Introspection
Name:		gobject-introspection
Version:	1.32.0
Release:	4
License:	GPLv2+, LGPLv2+, MIT
Group:		Development/C
Url:		http://live.gnome.org/GObjectIntrospection
Source0:	http://ftp.acc.umu.se/pub/GNOME/sources/%{name}/%{version}/%{name}-%{version}.tar.xz
# gi-find-deps.sh is a rpm helper for Provides and Requires. Script creates typelib()-style Provides/Requires.
Source1:	gi-find-deps.sh
Source2:	typelib.macros
Source3:	gobject-introspection-typelib.template
# PATCH-FIX-UPSTREAM g-ir-dep-tool.patch bgo#665672 dimstar@opensuse.org -- Add g-ir-dep-tool to get further automatic dependencies.
Patch0:	g-ir-dep-tool.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libtool
# this could be removed if the typelib stuff is backported
BuildRequires:	rpm >= 5.4.7-14
BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(cairo-gobject)
BuildRequires:	pkgconfig(gio-2.0)
BuildRequires:	pkgconfig(gio-unix-2.0)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gmodule-2.0)
BuildRequires:	pkgconfig(gobject-2.0)
BuildRequires:	pkgconfig(gthread-2.0)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(python)
# these are needed by the g-ir-dep-tool
%if !%{build_bootstrap}
BuildRequires:	pkgconfig(gobject-introspection-1.0) >= 1.32.0
BuildRequires:	gobject-introspection >= 1.32.0-2
BuildRequires:	%{_lib}atk-gir1.0 >= 2.4.0-1
%endif

Requires:	%{libname} = %{version}-%{release}
Conflicts:	%mklibname girepository 1.0 0 < 0.6.10-5
%rename		gir-repository

# Provide typelib() symbols based on gobject-introspection-typelib.template
# The template is checked during install if it matches the installed *.typelib files.
%if %{build_bootstrap}
%(cat %{SOURCE3} | awk '{ print "Provides: " $0}')
%endif

%description
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%package -n %{libname}
Group:		System/Libraries
Summary:	GObject Introspection shared library
Conflicts:	%{name} < 0.6.8-2

%description -n %{libname}
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%package -n %{develname}
Group:		Development/C
Summary:	GObject Introspection development libraries
# these two pkgs are needed for typelib requires generation
Requires:	%{name} = %{version}-%{release}
Requires:	%{_lib}atk-gir1.0 >= 2.4.0-1
Requires:	%{libname} = %{version}-%{release}
#gw /usr/bin/libtool is called in giscanner
Requires:	libtool
Provides:	libgirepository-devel = %{version}-%{release}
Provides:	girepository-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
The goal of the project is to describe the APIs and  collect them in
a uniform, machine readable format.

%prep
%setup -q
%apply_patches

%build
autoreconf -fi
%configure2_5x \
	--disable-static

%make

%install
%makeinstall_std
install -D %{SOURCE1} %{buildroot}%{_rpmhome}/gi-find-deps.sh
install -D %{SOURCE2} -m 0644 %{buildroot}%{_rpmhome}/macros.d/typelib

# comparing, if we provide all the symbols expected.
%if %{build_bootstrap}
ls %{buildroot}%{_libdir}/girepository-1.0/*.typelib | sh %{SOURCE1} -P > gobject-introspection-typelib.installed
diff -s %{SOURCE3} gobject-introspection-typelib.installed
%endif

%check
make check

%define typelibnames DBus-1.0 DBusGLib-1.0 GIRepository-2.0 GL-1.0 GLib-2.0 GModule-2.0 GObject-2.0 Gio-2.0 cairo-1.0 fontconfig-2.0 freetype2-2.0 libxml2-2.0 xfixes-4.0 xft-2.0 xlib-2.0 xrandr-1.3

%files
%doc README
%dir %{_libdir}/girepository-%{api}
%(for typelibname in %{typelibnames}; do
	echo "%{_libdir}/girepository-%{api}/$typelibname.typelib"
done)

%files -n %{libname}
%{_libdir}/libgirepository-%{api}.so.%{major}*

%files -n %{develname}
%doc ChangeLog TODO NEWS AUTHORS
%{_bindir}/g-ir-annotation-tool
%{_bindir}/g-ir-compiler
%{_bindir}/g-ir-dep-tool
%{_bindir}/g-ir-generate
%{_bindir}/g-ir-scanner
%{_libdir}/%{name}
%{_libdir}/libgirepository-%{api}.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/%{name}-%{api}
%{_datadir}/aclocal/*.m4
%{_datadir}/%{name}-%{api}
%{_datadir}/gtk-doc/html/gi
%dir %{_datadir}/gir-%{api}
%(for typelibname in %{typelibnames}; do
	echo "%{_datadir}/gir-%{api}/$typelibname.gir"
done)
%{_rpmhome}/gi-find-deps.sh
%{_rpmhome}/macros.d/typelib
%{_mandir}/man1/*
