#!/bin/bash

# Automatically find Provides and Requires for typelib() gobject-introspection bindings.
# Started with -R (Requires) or -P (Provides). -M selects rpm's multifile
# protocol: before the dependencies of a file, print ";<path>" using the
# path exactly as it was read. Files with no dependencies are omitted.
#
# RPM's default fileattr protocol is singlefile (one process per path).
# This script used to walk every typelib directory under /usr/lib on startup,
# so packages that never use GObject still paid that walk once per file.
# The walk now happens at most once per process, and only if a .typelib is
# actually being inspected. Python and JavaScript are recognised by a single
# fixed-string grep; the historic parsers run only on files that contain
# a relevant token. ELF objects are opened only far enough to read the
# section-name table, and gresource(1) runs only when a .gresource.* section
# is present (or the headers could not be trusted).
#
# Nested scans of files extracted from a GResource must be started WITHOUT
# -M. Their dependencies belong to the GResource or ELF that contained them.
#
# Copyright 2011 by Dominique Leuenberger, Amsterdam, Netherlands (dimstar [at] opensuse.org)
# This file is released under the GPLv2 or later.

# shellcheck disable=SC2086

function split_name_version {
	local base=$1
	local tsymbol=${base%-*}
	# imports.gi.Gdk.Settings.Foo is still the Gdk namespace.
	symbol=$(printf '%s\n' "$tsymbol" | awk -F. '{print $1}')
	version=${base#*-}
	# No '-' in the name: the expansion above leaves version == symbol.
	if [ "$tsymbol" = "$version" ]; then
		unset version
	fi
}

function split_name_version2 {
	symbol=$(printf '%s\n' "$1" | awk -F: '{sub(/^.*{/, "", $1); print $1}' | sed "s:[' ]::g")
	version=$(printf '%s\n' "$1" | awk -F: '{print $2}' | sed "s:[' ]::g")
}

# import 'gi://GeocodeGlib?version=2.0' (GNOME 43, e.g. GNOME Maps)
function split_name_versionjs_gi_name_version {
	symbol=$(printf '%s\n' "$1" | awk -F? '{print $1}')
	version=$(printf '%s\n' "$1" | awk -F? '/version=/ {print $2}' | sed 's/version=//')
}

# Print a dependency. In multifile mode, emit the owning path first.
function emit_begin {
	if [[ ${MULTIFILE:-0} == 1 && ${emitted:-0} == 0 ]]; then
		printf ';%s\n' "$current_file"
		emitted=1
	fi
}

function print_req_prov {
	emit_begin
	if [ -n "${version:-}" ]; then
		printf 'typelib(%s) = %s\n' "$symbol" "$version"
	else
		printf 'typelib(%s)\n' "$symbol"
	fi
}

function python_requires {
	local file=$1
	local module
	set -f
	for module in $(grep -h -a -P "^\s*from gi\.repository import (\w+)" -- "$file" | sed -e 's:#.*::' -e 's:raise ImportError.*::' -e 's:.*"from gi.repository import .*".*::' | sed -e 's,from gi.repository import,,' -r -e 's:\s+$::g' -e 's:\s+as\s+\w+::g' -e 's:,: :g'); do
		split_name_version "$module"
		print_req_prov
		# Temporarly disabled... this is not true if the python code is written for python3... And there seems no real 'way' to identify this.
		# echo "python-gobject >= 2.21.4"
	done
	for module in $(grep -h -a -P -o ".*(gi\.require_version\(['\"][^'\"]+['\"],\s*['\"][^'\"]+['\"]\))" -- "$file" | sed -e 's:#.*::' -e 's:.*gi.require_version::' -e "s:[()\"' ]::g" -e 's:,:-:'); do
		split_name_version "$module"
		print_req_prov
	done
	# python glue layers (/gi/overrides) import their typelibs slightly different
	for module in $(grep -h -a -P -o "=\s+(get_introspection_module\(['\"][^'\"]+['\"]\))" -- "$file" | sed -e 's:#.*::' -e 's:=.*get_introspection_module::' -e "s:[()\"' ]::g"); do
		split_name_version "$module"
		print_req_prov
	done
	set +f
}

function javascript_requires {
	local file=$1
	local module
	set -f
	# New import style in 3.32. grep -A2 matches the historic window.
	for module in $(grep -h -a -A2 -e 'const {' -- "$file" | paste -s -d ' ' | grep '} = imports.gi;' | sed 's/imports.gi;.*/imports.gi;/' | awk -F '[{}]' '{print $(NF>1?NF-1:"")}' | tr ',' '\n' | tr -d ' ' | awk -F ':' '{print $1}'); do
		split_name_version "$module"
		print_req_prov
	done
	# Old import style before 3.32.
	for module in $(grep -h -a -P -o "imports\.gi\.([^\s'\";]+)" -- "$file" | grep -v "imports\.gi\.version" | sed -r -e 's,\s+$,,g' -e 's,imports.gi.,,'); do
		split_name_version "$module"
		print_req_prov
	done
	for module in $(grep -h -a -P -o "imports\.gi\.versions.([^\s'\";]+)\s*=\s*['\"].+['\"]" -- "$file" | \
		sed -e 's:imports.gi.versions.::' -e "s:['\"]::g" -e 's:=:-:' -e 's: ::g'); do
		split_name_version "$module"
		print_req_prov
	done
	# import 'gi://GeocodeGlib?version=2.0'
	for module in $(grep -h -a -P -o "['\"]gi://([^'\"]+)" -- "$file" | sed "s|['\"]gi://||"); do
		split_name_versionjs_gi_name_version "$module"
		print_req_prov
	done
	# Polari: "const { Foo, Bar } = imports.gi;"
	for module in $(grep -h -a -E -o "\{ \w+(: \w+|, \w+)+ \} = imports.gi;" -- "$file" | \
		sed -r -e '0,/\w+:\s\w+/ s/:\s\w+//g' -e 's: = imports.gi;:: ; s:\{ :: ; s: \}:: ; s/,//g'); do
		split_name_version "$module"
		print_req_prov
	done
	set +f
	# pkg.require() dependencies are emitted here, not after every input
	# file, so multifile ";path" markers stay in input order.
	if grep -a -q -F 'pkg.require' -- "$file"; then
		javascript_pkg_one "$file"
	fi
}

function javascript_pkg_filter {
	# Placeholder. The per-file RECOGNIZED_MODULE_NAMES list is not applied;
	# gnome-weather's built-in modules are ignored unconditionally.
	# shellcheck disable=SC2034
	FILTER=('Lang' 'Mainloop' 'Signals' 'System' 'Params')
}

function javascript_pkg_one {
	local file=$1
	local pkg found i
	local oldIFS=$IFS
	local PKGS
	javascript_pkg_filter
	PKGS=$(pcre2grep -M "pkg.require\\(([^;])*" "$file" | grep -o -E "'?.*'?: '.*'" || true)
	set -f
	IFS=$'\n'
	for pkg in $PKGS; do
		split_name_version2 "$pkg"
		found=0
		for (( i=0 ; i<${#FILTER[@]} ; i++ )); do
			if [ "$symbol" = "${FILTER[$i]}" ]; then
				found=1
			fi
		done
		if [ "$found" -eq 0 ]; then
			print_req_prov
		fi
	done
	IFS=$oldIFS
	set +f
}

function typelib_requires {
	local oldIFS req module
	split_name_version "$(basename "$1" | sed 's,.typelib$,,')"
	add_typelib_dir "$(dirname "$1")"
	oldIFS=$IFS
	IFS=$'\n'
	for req in $(g-ir-inspect --print-shlibs --print-typelibs $symbol --version $version); do
		case $req in
			typelib:*)
				module=${req#typelib: }
				split_name_version "$module"
				print_req_prov
				;;
			shlib:*)
				emit_begin
				printf '%s%s\n' "${req#shlib: }" "${shlib_64:-}"
				;;
		esac
	done
	IFS=$oldIFS
}

# stdout: NUL-separated paths. printf is a bash builtin, so this is not
# subject to ARG_MAX the way an external exec of the whole list would be.
function stream_paths {
	local f
	for f in "$@"; do
		printf '%s\0' "$f"
	done
}

# g-ir-inspect looks typelibs up by name. The default search path already
# covers /usr/lib{,64}/girepository-1.0; private copies and typelibs that
# exist only in this build root have to be added. Identical directory set
# and sort order to the historic find|dirname|sort --unique walk.
function setup_typelib_path {
	[[ -n ${_GI_FIND_DEPS_PATH_READY:-} ]] && return 0
	_GI_FIND_DEPS_PATH_READY=1
	local -a roots=()
	local candidate real seen dir
	add_root() {
		[[ -d $1 ]] || return 0
		real=$(readlink -f -- "$1" 2>/dev/null || true)
		[[ -n $real && -d $real ]] || return 0
		for seen in "${roots[@]}"; do
			[[ $seen == "$real" ]] && return 0
		done
		roots+=("$real")
	}
	if [[ -n ${RPM_BUILD_ROOT:-} ]]; then
		add_root "${RPM_BUILD_ROOT}/usr/lib64"
		add_root "${RPM_BUILD_ROOT}/usr/lib"
	fi
	add_root /usr/lib64
	add_root /usr/lib
	if [[ ${#roots[@]} -gt 0 ]]; then
		while IFS= read -r dir; do
			[[ -n $dir ]] || continue
			GI_TYPELIB_PATH="${GI_TYPELIB_PATH:-}:$dir"
		done < <(find "${roots[@]}" -name '*.typelib' -printf '%h\n' 2>/dev/null | sort -u)
	fi
	export GI_TYPELIB_PATH
}

function add_typelib_dir {
	local dir=$1
	[[ -n $dir ]] || return 0
	case ":${GI_TYPELIB_PATH:-}:" in
		*":$dir:"*) ;;
		*) GI_TYPELIB_PATH="${GI_TYPELIB_PATH:-}:$dir" ;;
	esac
	export GI_TYPELIB_PATH
}

function gresources_requires {
	local file=$1
	local list tmpdir resource out
	[[ -n ${gresourcecmd:-} ]] || return 0
	[[ -f $file ]] || return 0
	list=$("$gresourcecmd" list "$file" 2>/dev/null || true)
	[[ -n $list ]] || return 0
	tmpdir=$(mktemp -d)
	# shellcheck disable=SC2086
	for resource in $list; do
		mkdir -p "$tmpdir/$(dirname "$resource")"
		"$gresourcecmd" extract "$file" "$resource" > "$tmpdir/$resource" || true
	done
	# -R without -M: dependencies are printed bare and attributed to $file.
	out=$(find "$tmpdir" -type f | sort | bash "$0" -R || true)
	rm -rf "$tmpdir"
	if [[ -n $out ]]; then
		emit_begin
		printf '%s\n' "$out"
	fi
}

# Classify paths that the suffix did not already explain.
# One line per file: <kind>\t<path>
# kind is elf (no GResource section), elfg (has one), elfq (headers not
# trustworthy: probe with gresource), python, javascript, other, or skip.
function run_classifier {
	python -u -c '
import os, stat, struct, sys

SHT_PROGBITS = 1

def elf_has_gresource(fh):
    """True/False, or None when the headers should not be trusted."""
    try:
        fh.seek(0)
        ident = fh.read(64)
        if len(ident) < 20 or ident[:4] != b"\x7fELF":
            return None
        ei_class = ident[4]
        ei_data = ident[5]
        if ei_data == 1:
            end = "<"
        elif ei_data == 2:
            end = ">"
        else:
            return None
        if ei_class == 2:
            if len(ident) < 64:
                return None
            e_shoff, _, _, _, _, e_shentsize, e_shnum, e_shstrndx = struct.unpack_from(end + "QIHHHHHH", ident, 40)
            hdr_min = 64
            str_off = 24
            str_fmt = end + "QQ"
        elif ei_class == 1:
            if len(ident) < 52:
                ident += fh.read(52 - len(ident))
            if len(ident) < 52:
                return None
            e_shoff, _, _, _, _, e_shentsize, e_shnum, e_shstrndx = struct.unpack_from(end + "IIHHHHHH", ident, 32)
            hdr_min = 40
            str_off = 16
            str_fmt = end + "II"
        else:
            return None
        if (e_shoff == 0 or e_shnum == 0 or e_shentsize < hdr_min
                or e_shstrndx in (0, 0xFFFF) or e_shstrndx >= e_shnum
                or e_shnum > 100000 or e_shentsize > 4096):
            return None
        fh.seek(e_shoff + e_shstrndx * e_shentsize)
        shstr_hdr = fh.read(e_shentsize)
        if len(shstr_hdr) < str_off + struct.calcsize(str_fmt):
            return None
        sh_offset, sh_size = struct.unpack_from(str_fmt, shstr_hdr, str_off)
        if sh_offset <= 0 or sh_size <= 0 or sh_size > 10_000_000:
            return None
        fh.seek(sh_offset)
        strtab = fh.read(sh_size)
        if len(strtab) != sh_size:
            return None
        if b".gresource." not in strtab:
            return False
        total = e_shentsize * e_shnum
        fh.seek(e_shoff)
        blob = fh.read(total)
        if len(blob) != total:
            return None
        for i in range(e_shnum):
            off = i * e_shentsize
            sh_name, sh_type = struct.unpack_from(end + "II", blob, off)
            if sh_type != SHT_PROGBITS or sh_name >= len(strtab):
                continue
            endn = strtab.find(b"\x00", sh_name)
            name = strtab[sh_name:endn if endn != -1 else None]
            if name.startswith(b".gresource."):
                return True
        return False
    except Exception:
        return None

def shebang_kind(head):
    if not head.startswith(b"#!"):
        return None
    line = head.split(b"\n", 1)[0][2:].strip()
    for tok in line.split():
        if tok.startswith(b"-"):
            continue
        base = tok.rsplit(b"/", 1)[-1]
        if base in (b"env", b"nice", b"nohup", b"stdbuf", b"busybox", b"timeout"):
            continue
        if base.startswith(b"python"):
            return "python"
        if base == b"gjs" or base.startswith(b"gjs-"):
            return "javascript"
        return None
    return None

def classify(raw):
    path = os.fsdecode(raw)
    try:
        st = os.stat(raw)
    except OSError:
        return "skip", path
    if not stat.S_ISREG(st.st_mode):
        return "skip", path
    try:
        fh = open(raw, "rb")
    except OSError:
        return "skip", path
    with fh:
        head = fh.read(512)
        if head.startswith(b"\x7fELF"):
            found = elf_has_gresource(fh)
            if found is True:
                return "elfg", path
            if found is False:
                return "elf", path
            return "elfq", path
        kind = shebang_kind(head)
        if kind:
            return kind, path
    return "other", path

data = sys.stdin.buffer.read().split(b"\0")
for raw in data:
    if not raw:
        continue
    try:
        kind, path = classify(raw)
    except Exception as exc:
        sys.stderr.write("gi-find-deps: %s\n" % exc)
        kind, path = "skip", os.fsdecode(raw)
    sys.stdout.write("%s\t%s\n" % (kind, path))
' 
}

function note_classified {
	local k p
	while IFS=$'\t' read -r k p || [[ -n ${k:-} ]]; do
		[[ -n ${k:-} ]] || continue
		kind["$p"]=$k
		case $k in
			python) py_check+=("$p") ;;
			javascript) js_check+=("$p") ;;
			other) other_check+=("$p") ;;
			elfg|elfq) gres_hit["$p"]=1 ;;
		esac
	done
}

# file(1) fallback for extensionless files, and for every unknown file when
# python is unavailable. Matches the historic "*Python*script* /
# *JavaScript*source* / *ELF*" dispatch. gjs shebangs are included here too:
# file(1) reports them as "Java source", which dropped real imports.gi users.
function classify_with_file {
	local f desc line
	for f in "$@"; do
		if [[ ! -f $f ]]; then
			kind["$f"]=skip
			continue
		fi
		# ELF magic. file(1) would say ELF; gresource decides the rest.
		if [[ $(od -An -t x1 -N 4 -- "$f" 2>/dev/null) == *"7f 45 4c 46"* ]]; then
			kind["$f"]=elfq
			gres_hit["$f"]=1
			continue
		fi
		IFS= read -r line < "$f" || true
		case $line in
			\#\!*python*)
				kind["$f"]=python
				py_check+=("$f")
				continue
				;;
			\#\!*gjs*)
				kind["$f"]=javascript
				js_check+=("$f")
				continue
				;;
		esac
		desc=$(file -b -- "$f" 2>/dev/null || true)
		case $desc in
			*[Pp]ython*script*)
				kind["$f"]=python
				py_check+=("$f")
				;;
			*JavaScript*source*)
				kind["$f"]=javascript
				js_check+=("$f")
				;;
			*ELF*)
				kind["$f"]=elfq
				gres_hit["$f"]=1
				;;
			*)
				kind["$f"]=other
				other_check+=("$f")
				;;
		esac
	done
}

function collect_marker_hits {
	# $1 is an associative-array name in the caller. Remaining args up to --
	# are grep -e options. After -- are paths.
	local -n dest_ref=$1
	shift
	local -a patterns=()
	local hit
	while [[ $# -gt 0 && $1 != "--" ]]; do
		patterns+=("$1")
		shift
	done
	[[ ${1:-} == "--" ]] && shift
	[[ $# -gt 0 ]] || return 0
	while IFS= read -r hit; do
		[[ -n $hit ]] || continue
		dest_ref["$hit"]=1
	done < <(stream_paths "$@" | xargs -0 -r grep -a -F -l "${patterns[@]}" -- 2>/dev/null || true)
}

function find_provides {
	local file
	while IFS= read -r file || [[ -n ${file:-} ]]; do
		[[ -n $file ]] || continue
		case $file in
			*.typelib)
				current_file=$file
				emitted=0
				split_name_version "$(basename "$file" | sed 's,.typelib$,,')"
				print_req_prov
				;;
		esac
	done
}

function dispatch_file {
	local f=$1
	current_file=$f
	emitted=0
	case ${kind[$f]:-} in
		typelib)
			typelib_requires "$f"
			;;
		py|python)
			[[ -n ${py_hit[$f]:-} ]] && python_requires "$f"
			;;
		js|javascript)
			[[ -n ${js_hit[$f]:-} ]] && javascript_requires "$f"
			;;
		gresource)
			gresources_requires "$f"
			;;
		elfg|elfq)
			[[ -n ${gres_hit[$f]:-} ]] && gresources_requires "$f"
			;;
		other)
			if [[ -n ${py_hit[$f]:-} ]]; then
				python_requires "$f"
			elif [[ -n ${js_hit[$f]:-} ]]; then
				javascript_requires "$f"
			fi
			;;
	esac
}

function find_requires {
	local -a files=() py_check=() js_check=() other_check=() need_magic=()
	local -A kind=() py_hit=() js_hit=() gres_hit=()
	local file saw_typelib=0 cls
	local -a other_hits=()

	while IFS= read -r file || [[ -n ${file:-} ]]; do
		[[ -n $file ]] || continue
		files+=("$file")
		case $file in
			*.typelib)
				kind["$file"]=typelib
				saw_typelib=1
				;;
			*.py)
				if [[ -f $file ]]; then
					kind["$file"]=py
					py_check+=("$file")
				fi
				;;
			*.js)
				if [[ -f $file ]]; then
					kind["$file"]=js
					js_check+=("$file")
				fi
				;;
			*.gresource)
				if [[ -f $file ]]; then
					kind["$file"]=gresource
				fi
				;;
			*)
				need_magic+=("$file")
				;;
		esac
	done

	if [[ ${#need_magic[@]} -gt 0 ]]; then
		cls=$(mktemp)
		if stream_paths "${need_magic[@]}" | run_classifier >"$cls"; then
			note_classified <"$cls"
		else
			classify_with_file "${need_magic[@]}"
		fi
		rm -f "$cls"
	fi

	collect_marker_hits py_hit -e gi.repository -e gi.require_version -e get_introspection_module -- "${py_check[@]}"
	collect_marker_hits js_hit -e imports.gi -e 'gi://' -e pkg.require -- "${js_check[@]}"

	# Extensionless (and other suffix-less) files: grep first, and only run
	# file(1) on the few that actually mention a binding. Shebang matches
	# were already classified and are not in other_check.
	if [[ ${#other_check[@]} -gt 0 ]]; then
		while IFS= read -r file; do
			[[ -n $file ]] && other_hits+=("$file")
		done < <(stream_paths "${other_check[@]}" | xargs -0 -r grep -a -F -l \
			-e gi.repository -e gi.require_version -e get_introspection_module \
			-e imports.gi -e 'gi://' -e pkg.require -- 2>/dev/null || true)
		for file in "${other_hits[@]}"; do
			local desc
			desc=$(file -b -- "$file" 2>/dev/null || true)
			case $desc in
				*[Pp]ython*script*)
					if grep -a -q -F -e gi.repository -e gi.require_version -e get_introspection_module -- "$file"; then
						py_hit["$file"]=1
					fi
					;;
				*JavaScript*source*)
					if grep -a -q -F -e imports.gi -e 'gi://' -e pkg.require -- "$file"; then
						js_hit["$file"]=1
					fi
					;;
				*ELF*)
					gres_hit["$file"]=1
					kind["$file"]=elfq
					;;
			esac
		done
	fi

	if [[ $saw_typelib == 1 ]]; then
		setup_typelib_path
	fi

	for file in "${files[@]}"; do
		dispatch_file "$file"
	done
}

function inList() {
	local word
	for word in $1; do
		[[ $word == "$2" ]] && return 0
	done
	return 1
}

# Confer with /usr/lib/rpm/platforms
x64bitarch="aarch64 loongarch64 mips64 mips64el mips64r6 mips64r6el ppc64 ppc64le riscv64 s390x sparc64 x86_64"
shlib_64=
if inList "$x64bitarch" "${HOSTTYPE}"; then
	shlib_64="()(64bit)"
fi

gresourcecmd=$(command -v gresource 2>/dev/null || true)

mode=
MULTIFILE=0
for arg in "$@"; do
	case $arg in
		-P|-R) mode=$arg ;;
		-M) MULTIFILE=1 ;;
	esac
done

case $mode in
	-P) find_provides ;;
	-R) find_requires ;;
esac
exit 0
