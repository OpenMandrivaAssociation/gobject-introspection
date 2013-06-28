#!/bin/sh

# Automatically find Provides and Requires for typelib() gobject-introspection bindings.
# can be started with -R (Requires) and -P (Provides)

# Copyright 2011 by Dominique Leuenberger, Amsterdam, Netherlands (dimstar [at] opensuse.org)
# This file is released under the GPLv2 or later.

function split_name_version {
base=$1
tsymbol=${base%-*}
# Sometimes we get a Requires on Gdk.Settings.foo, bebause you can directly use imports.gi.Gdk.Settings.Foo in Javascript.
# We know that the symbol in this case is called Gdk, so we cut everything after the . away.
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

function python_requires {
	for module in $(grep -h -P "from gi\.repository import (\w+)" $1 | sed -e 's:#.*::' -e 's:raise ImportError.*::' -e 's:.*"from gi.repository import Foo".*::' | sed -e 's,from gi.repository import,,' -r -e 's:\s+$::g' -e 's:\s+as\s+\w+::g' -e 's:,: :g'); do
		split_name_version $module
		print_req_prov
		# Temporarly disabled... this is not true if the python code is written for python3... And there seems no real 'way' to identify this.
		# echo "python-gobject >= 2.21.4"
	done
	for module in $(grep -h -P -o "(gi\.require_version\(['\"][^'\"]+['\"],\s*['\"][^'\"]+['\"]\))" $1 | sed -e 's:gi.require_version::' -e "s:[()\"' ]::g" -e 's:,:-:'); do
		split_name_version $module
		print_req_prov
	done
}

function javascript_requires {
	for module in $(grep -h -P -o "imports\.gi\.([^\s'\";]+)" $1 | grep -v "imports\.gi\.version" | sed -r -e 's,\s+$,,g' -e 's,imports.gi.,,'); do
		split_name_version $module
		print_req_prov
	done
	for module in $(grep -h -P -o "imports\.gi\.versions.([^\s'\";]+)\s*=\s*['\"].+['\"]" $1 | \
		sed -e 's:imports.gi.versions.::' -e "s:['\"]::g" -e 's:=:-:' -e 's: ::g'); do
		split_name_version $module
		print_req_prov
	done

}

function typelib_requires {
	split_name_version $(basename $1 | sed 's,.typelib$,,')
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
}

function find_requires {
# Currently, we detect:
# - in python:
#   . from gi.repository import foo [Unversioned requirement of 'foo']
#   . from gi.repository import foo-1.0 [versioned requirement]
#   . gi.require_version('Gtk', '3.0') (To specify a version.. there is still an import needed)
#   . And we do not stumble over:
#     from gi.repository import foo as _bar
#     from gi.repository import foo, bar
# - in JS:
#   . imports.gi.foo; [unversioned requirement of 'foo']
#   . imports.gi.goo-1.0; [versioned requirement]
#   . imports.gi.versions.Gtk = '3.0';
#   . The imports can be listed on one line, and we catch them.

while read file; do
	case $file in
		*.js)
			javascript_requires "$file"
			;;
		*.py)
			python_requires "$file"
			;;
		*.typelib)
			typelib_requires "$file"
			;;
		*)
			case $(file -b $file) in
				Python\ script*)
					python_requires "$file"
					;;
			esac
			;;
	esac
done
}

function inList() {
  for word in $1; do
    [[ "$word" = "$2" ]] && return 0
  done
  return 1
}

x64bitarch="x86_64 ppc64 s390x ia64 aarch64"

for path in \
	$(for tlpath in \
	$(find ${RPM_BUILD_ROOT}/usr/lib64 ${RPM_BUILD_ROOT}/usr/lib /usr/lib64 /usr/lib -name '*.typelib' 2>/dev/null); do
        	dirname $tlpath; done | uniq ); do
	export GI_TYPELIB_PATH=$GI_TYPELIB_PATH:$path
done

if inList "$x64bitarch" "${HOSTTYPE}"; then
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

