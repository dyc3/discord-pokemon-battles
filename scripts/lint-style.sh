#!/bin/bash

usage() {
	cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-w]

Code and docstring style enforcement.

Available options:

-h, --help      Print this help and exit
-w, --write     Automatically format code in place
EOF
	exit
}

parse_params() {
	# default values of variables set from params

	while :; do
		case "${1-}" in
		-h | --help) usage ;;
		-w | --write) WRITE=1 ;;
		-q | --quiet) QUIET=1 ;;
		-?*) echo "Unknown option: $1"; exit ;;
		*) break ;;
		esac
		shift
	done

	args=("$@")

	# check required params and arguments

	return 0
}

parse_params "$@"

yapf_opts=(--recursive --parallel)
if [[ -n "$QUIET" ]]; then
	yapf_opts+=("--quiet")
elif [[ -n "$WRITE" ]]; then
	yapf_opts+=("--in-place")
fi
yapf "${yapf_opts[@]}" .
