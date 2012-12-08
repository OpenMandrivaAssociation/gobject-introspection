#!/bin/sh

# Automatically find Provides and Requires for typelib() gobject-introspection bindings.
# can be started with -R (Requires) and -P (Provides)

# Copyright 2011 by Dominique Leuenberger, Amsterdam, Netherlands (dimstar [at] opensuse.org)
# This file is released under the GPLv2 or later.

function split_name_version {
base=$1
tsymbol=${base%-*}
# Sometimes we get a Requires on Gdk.Settings.foo, bebause you can directly use imports.gi.Gdk.Settings.Foo in Javascript.
# We know that the symbol in this case is call Gdk, so we cut everything after the . away.
symbol=$(echo $tsymbol | awk -F. '{print $1}')
version=${base#*-}
# In case there is no '-' in the filename, then the split above 'fails' and version == symbol (thus: no version specified)
if [ "$tsymbol" = "$version" ]; then
	unset version
fi
}

function print_req_prov {
echo -n "typelib($symbol)"
if [ ! -z "$version" ]; then
	echo " = ${version}"
else
	echo ""
fi
}

function find_provides {
while read file; do
	case $file in
		*.typelib)
			split_name_version $(basename $file | sed 's,.typelib$,,')
			print_req_prov
			;;
	esac
done
}

function find_requires {
# FIXME: There are multiple ways gi bindings can be imported. We only catch the 'basic' one
# Currently, we detect:
# - in python:
#   . from gi.repository import foo [Unversioned requirement of 'foo']
#   . from gi.repository import foo-1.0 [versioned requirement]
#   . And we do not stumble over:
#     from gi.repository import foo as _bar
#     from gi.repository import foo, bar
# - in JS:
#   . imports.gi.foo; [unversioned requirement of 'foo']
#   . imports.gi.goo-1.0; [versioned requirement]
#   . The imports can be listed on one line, and we catch them.
# Forms currently not detected:
# - js: imports.gi.versions.Gtk = '3.0';
# - py: gi.require_version('Gtk', '3.0')

while read file; do
	case $file in
		*.js)
			for module in $(grep -h -P -o "imports.gi.([^\s'\";]+)" $file | grep -v "imports.gi.version" | sed -r -e 's,\s+$,,g' -e 's,imports.gi.,,'); do
				split_name_version $module
				print_req_prov
			done
			;;
	      *.py)
		        for module in $(grep -h -P "from gi.repository import (\w+)" $file | sed -e 's:#.*::' -e 's:raise ImportError.*::' | sed -e 's,from gi.repository import,,' -r -e 's:\s+$::g' -e 's:\s+as\s+\w+::g' -e 's:,: :g'); do
				split_name_version $module
				print_req_prov
			done
			;;
	      *.typelib)
			split_name_version $(basename $file | sed 's,.typelib$,,')
			oldIFS=$IFS
			IFS=$'\n'
			for req in $(g-ir-dep-tool $symbol $version); do
				case $req in
					typelib:*)
						module=${req#typelib: }
						split_name_version $module
						print_req_prov
						;;
					shlib:*)
						echo "${req#shlib: }${shlib_64}"
						;;
				esac
			done
			IFS=$oldIFS
			;;
	esac
done
}

# for rpm5.org RPM_BUILD_ROOT isnt exported here
# so we pass buildroot as a variable in the typelib requires macro
RPM_BUILD_ROOT=$2
for path in \
	$(for tlpath in \
	$(find ${RPM_BUILD_ROOT}/usr/lib64 ${RPM_BUILD_ROOT}/usr/lib /usr/lib64 /usr/lib -name '*.typelib' 2>/dev/null); do
        	dirname $tlpath; done | uniq ); do
	export GI_TYPELIB_PATH=$GI_TYPELIB_PATH:$path
done

if [ "${HOSTTYPE}" == "x86_64" -o "${HOSTTYPE}" == "ppc64" -o "${HOSTTYPE}" == "s390x" -o "${HOSTTYPE}" == "ia64" ]; then
	shlib_64="()(64bit)"
fi
case $1 in
	-P)	
		find_provides
		;;
	-R)
		find_requires
		;;
esac

