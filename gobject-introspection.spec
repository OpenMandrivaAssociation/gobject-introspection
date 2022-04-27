%define url_ver %(echo %{version}|cut -d. -f1,2)

%define build_bootstrap 1
%define api 1.0
%define major 1
%define libname %mklibname girepository %{api} %{major}
%define devname %mklibname -d girepository

Summary:	GObject Introspection
Name:		gobject-introspection
Version:	1.72.0
Release:	2
License:	GPLv2+, LGPLv2+, MIT
Group:		Development/C
Url:		http://live.gnome.org/GObjectIntrospection
Source0:	http://ftp.gnome.org/pub/GNOME/sources/gobject-introspection/%{url_ver}/%{name}-%{version}.tar.xz
# gi-find-deps.sh is a rpm helper for Provides and Requires. Script creates typelib()-style Provides/Requires.
Source1:	gi-find-deps.sh
Source2:	typelib.attr
Source3:	gobject-introspection-typelib.template
#Patch1:		gobject-introspection-1.54.1-lto.patch
Patch2:		python3-linking.patch

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libtool
BuildRequires:	meson
# this could be removed if the typelib stuff is backported
BuildRequires:	rpm >= 2:4.14.1-0.20
BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(cairo-gobject)
BuildRequires:	pkgconfig(gio-2.0)
BuildRequires:	pkgconfig(gio-unix-2.0)
BuildRequires:	pkgconfig(glib-2.0) >= 2.54.0
BuildRequires:	pkgconfig(gmodule-2.0)
BuildRequires:	pkgconfig(gobject-2.0)
BuildRequires:	pkgconfig(gthread-2.0)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(python)
#BuildRequires:  pkgconfig(vapigen)
BuildRequires:	python-mako
BuildRequires:	python-markdown
BuildRequires:	docbook-dtd-xml
BuildRequires:	gtk-doc
BuildRequires:	chrpath
# these are needed by the g-ir-dep-tool
%if !%{build_bootstrap}
BuildRequires:	pkgconfig(gobject-introspection-1.0) >= 1.32.0
BuildRequires:	gobject-introspection >= 1.32.0-2
%endif

Requires:	%{libname} = %{EVRD}
Conflicts:	%mklibname girepository 1.0 0 < 0.6.10-5
%rename		gir-repository

# Provide typelib() symbols based on gobject-introspection-typelib.template
# The template is checked during install if it matches the installed *.typelib files.
%if %{build_bootstrap}
%(cat %{SOURCE3} | awk '{ print "Provides: " $0}')
%endif

%description
The goal of the project is to describe the APIs and collect them in
a uniform, machine readable format.

%package -n	%{libname}
Group:		System/Libraries
Summary:	GObject Introspection shared library
Conflicts:	%{name} < 0.6.8-2
Requires:	%{name} >= %{EVRD}

%description -n %{libname}
The goal of the project is to describe the APIs and collect them in
a uniform, machine readable format.

#---------------------------------------------------------------
%define girglibname %mklibname glib-gir 2.0

%package -n %{girglibname}
Summary:	GObject Introspection interface description for glib
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2
Provides:	glib-gir = %{EVRD}
Requires:	%{name} >= %{EVRD}
Requires:	glib2
Requires:	gio2.0

%description -n %{girglibname}
GObject Introspection interface description for glib.

%files -n %{girglibname}
%{_libdir}/girepository-1.0/GLib-2.0.typelib
%{_libdir}/girepository-1.0/GModule-2.0.typelib
%{_libdir}/girepository-1.0/GObject-2.0.typelib
%{_libdir}/girepository-1.0/Gio-2.0.typelib

#---------------------------------------------------------------
%define girdbusname %mklibname dbus-gir 1.0

%package -n %{girdbusname}
Summary:	GObject Introspection interface description for dbus
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girdbusname}
GObject Introspection interface description for dbus.

%files -n %{girdbusname}
%{_libdir}/girepository-1.0/DBus-1.0.typelib

#---------------------------------------------------------------
%define girdbusglibname %mklibname dbusglib-gir 1.0

%package -n %{girdbusglibname}
Summary:	GObject Introspection interface description for dbusglib
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girdbusglibname}
GObject Introspection interface description for dbusglib.

%files -n %{girdbusglibname}
%{_libdir}/girepository-1.0/DBusGLib-1.0.typelib

#---------------------------------------------------------------
%define girgirepositoryname %mklibname girepository-gir 2.0

%package -n %{girgirepositoryname}
Summary:	GObject Introspection interface description for girepository
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2
Requires:	%{libname} = %{EVRD}

%description -n %{girgirepositoryname}
GObject Introspection interface description for girepository.

%files -n %{girgirepositoryname}
%{_libdir}/girepository-1.0/GIRepository-2.0.typelib

#---------------------------------------------------------------
%define girglname %mklibname gl-gir 1.0

%package -n %{girglname}
Summary:	GObject Introspection interface description for OpenGL
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girglname}
GObject Introspection interface description for OpenGL.

%files -n %{girglname}
%{_libdir}/girepository-1.0/GL-1.0.typelib

#---------------------------------------------------------------
%define gircaironame %mklibname cairo-gir 1.0

%package -n %{gircaironame}
Summary:	GObject Introspection interface description for cairo
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{gircaironame}
GObject Introspection interface description for cairo.

%files -n %{gircaironame}
%{_libdir}/girepository-1.0/cairo-1.0.typelib

#---------------------------------------------------------------
%define girfontconfigname %mklibname fontconfig-gir 2.0

%package -n %{girfontconfigname}
Summary:	GObject Introspection interface description for fontconfig
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girfontconfigname}
GObject Introspection interface description for fontconfig.

%files -n %{girfontconfigname}
%{_libdir}/girepository-1.0/fontconfig-2.0.typelib

#---------------------------------------------------------------
%define girfreetypename %mklibname freetype-gir 2.0

%package -n %{girfreetypename}
Summary:	GObject Introspection interface description for freetype
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girfreetypename}
GObject Introspection interface description for freetype.

%files -n %{girfreetypename}
%{_libdir}/girepository-1.0/freetype2-2.0.typelib

#---------------------------------------------------------------

%define girvulkanname %mklibname vulkan-gir 1.0

%package -n %{girvulkanname}
Summary:	GObject Introspection interface description for Vulkan
Group:		System/Libraries

%description -n %{girvulkanname}
GObject Introspection interface description for Vulkan.

%files -n %{girvulkanname}
%{_libdir}/girepository-1.0/Vulkan-1.0.typelib

#---------------------------------------------------------------
%define girlibxml2name %mklibname xml2-gir 2.0

%package -n %{girlibxml2name}
Summary:	GObject Introspection interface description for libxml2
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2
Obsoletes:	%{_lib}libxml2-gir2.0 < 1.36.0-2

%description -n %{girlibxml2name}
GObject Introspection interface description for libxml2.

%files -n %{girlibxml2name}
%{_libdir}/girepository-1.0/libxml2-2.0.typelib

#---------------------------------------------------------------
%define girxfixesname %mklibname xfixes-gir 4.0

%package -n %{girxfixesname}
Summary:	GObject Introspection interface description for xfixes
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girxfixesname}
GObject Introspection interface description for xfixes.

%files -n %{girxfixesname}
%{_libdir}/girepository-1.0/xfixes-4.0.typelib

#---------------------------------------------------------------
%define girxftname %mklibname xft-gir 2.0

%package -n %{girxftname}
Summary:	GObject Introspection interface description for xft
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girxftname}
GObject Introspection interface description for xft.

%files -n %{girxftname}
%{_libdir}/girepository-1.0/xft-2.0.typelib

#---------------------------------------------------------------
%define girxlibname %mklibname xlib-gir 2.0

%package -n %{girxlibname}
Summary:	GObject Introspection interface description for xlib
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girxlibname}
GObject Introspection interface description for xlib.

%files -n %{girxlibname}
%{_libdir}/girepository-1.0/xlib-2.0.typelib

#---------------------------------------------------------------
%define girxrandrname %mklibname xrandr-gir 1.3

%package -n %{girxrandrname}
Summary:	GObject Introspection interface description for xrandr
Group:		System/Libraries
Conflicts:	%{name} < 1.36.0-2

%description -n %{girxrandrname}
GObject Introspection interface description for xrandr.

%files -n %{girxrandrname}
%{_libdir}/girepository-1.0/xrandr-1.3.typelib

#---------------------------------------------------------------
%define girwin32name %mklibname win32-gir 1.0

%package -n %{girwin32name}
Summary:	GObject Introspection interface description for win32
Group:		System/Libraries

%description -n %{girwin32name}
GObject Introspection interface description for win32.

%files -n %{girwin32name}
%{_libdir}/girepository-1.0/win32-1.0.typelib

%package -n %{devname}
Group:		Development/C
Summary:	GObject Introspection development libraries
# these two pkgs are needed for typelib requires generation
Requires:	%{name} = %{EVRD}
Requires:	%{libname} = %{EVRD}
#gw /usr/bin/libtool is called in giscanner
Requires:	libtool
# gi-find-deps.sh uses pcregrep
Requires:	pcre
Requires:	file
Requires:	pkgconfig(python)
Provides:	libgirepository-devel = %{EVRD}
Provides:	girepository-devel = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	%{girglibname} = %{EVRD}
Requires:	%{girdbusname} = %{EVRD}
Requires:	%{girdbusglibname} = %{EVRD}
Requires:	%{girgirepositoryname} = %{EVRD}
Requires:	%{girglname} = %{EVRD}
Requires:	%{gircaironame} = %{EVRD}
Requires:	%{girfontconfigname} = %{EVRD}
Requires:	%{girfreetypename} = %{EVRD}
Requires:	%{girvulkanname} = %{EVRD}
Requires:	%{girlibxml2name} = %{EVRD}
Requires:	%{girxfixesname} = %{EVRD}
Requires:	%{girxftname} = %{EVRD}
Requires:	%{girxlibname} = %{EVRD}
Requires:	%{girxrandrname} = %{EVRD}
Requires:	%{girwin32name} = %{EVRD}

%description -n %{devname}
The goal of the project is to describe the APIs and collect them in
a uniform, machine readable format.

%prep
%autosetup -p1

%build
%meson -Ddoctool=enabled -Dgtk_doc=true -Dpython=%{__python3}
%meson_build

%install
%meson_install

install -D %{SOURCE1} %{buildroot}%{_rpmconfigdir}/gi-find-deps.sh
install -D %{SOURCE2} -m 0644 %{buildroot}%{_fileattrsdir}/typelib.attr

# comparing, if we provide all the symbols expected.
%if %{build_bootstrap}
ls %{buildroot}%{_libdir}/girepository-1.0/*.typelib | sh %{SOURCE1} -P |sort > gobject-introspection-typelib.installed
cat %{SOURCE3} |sort >gobject-introspection-typelib.reference
diff -u -s gobject-introspection-typelib.reference gobject-introspection-typelib.installed
%endif

# Remove lib64 rpaths
chrpath --delete %{buildroot}%{_bindir}/g-ir-compiler
chrpath --delete %{buildroot}%{_bindir}/g-ir-generate
chrpath --delete %{buildroot}%{_bindir}/g-ir-inspect

%files
%doc NEWS TODO
%dir %{_libdir}/girepository-%{api}

%files -n %{libname}
%{_libdir}/libgirepository-%{api}.so.%{major}*

%files -n %{devname}
%{_libdir}/libgirepository-%{api}.so
%{_libdir}/pkgconfig/gobject-introspection-%{api}.pc
%{_libdir}/pkgconfig/gobject-introspection-no-export-%{api}.pc
%{_includedir}/%{name}-%{api}
%{_datadir}/aclocal/*.m4
%{_datadir}/%{name}-%{api}
%{_bindir}/g-ir-*
%{_libdir}/%{name}
%{_datadir}/gtk-doc/html/gi
%dir %{_datadir}/gir-%{api}
%{_datadir}/gir-%{api}/gir-1.2.rnc
%{_datadir}/gir-%{api}/DBus-1.0.gir
%{_datadir}/gir-%{api}/DBusGLib-1.0.gir
%{_datadir}/gir-%{api}/GIRepository-2.0.gir
%{_datadir}/gir-%{api}/GL-1.0.gir
%{_datadir}/gir-%{api}/GLib-2.0.gir
%{_datadir}/gir-%{api}/GModule-2.0.gir
%{_datadir}/gir-%{api}/GObject-2.0.gir
%{_datadir}/gir-%{api}/Gio-2.0.gir
%{_datadir}/gir-%{api}/cairo-1.0.gir
%{_datadir}/gir-%{api}/fontconfig-2.0.gir
%{_datadir}/gir-%{api}/freetype2-2.0.gir
%{_datadir}/gir-%{api}/Vulkan-1.0.gir
%{_datadir}/gir-%{api}/libxml2-2.0.gir
%{_datadir}/gir-%{api}/xfixes-4.0.gir
%{_datadir}/gir-%{api}/xft-2.0.gir
%{_datadir}/gir-%{api}/xlib-2.0.gir
%{_datadir}/gir-%{api}/xrandr-1.3.gir
%{_datadir}/gir-%{api}/win32-1.0.gir
%{_mandir}/man1/*
%{_rpmconfigdir}/gi-find-deps.sh
%{_rpmconfigdir}/fileattrs/typelib.attr
