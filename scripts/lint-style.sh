#!/bin/bash

usage() {
	cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-q]

Code and docstring style enforcement.

Available options:

-h, --help      Print this help and exit
EOF
	exit
}

parse_params() {
	# default values of variables set from params

	while :; do
		case "${1-}" in
		-h | --help) usage ;;
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
	yapf_opts+=(--quiet)
else
	yapf_opts+=(--verbose --in-place)
fi
yapf "${yapf_opts[@]}" . || exit 1
pydocstyle || exit 2
