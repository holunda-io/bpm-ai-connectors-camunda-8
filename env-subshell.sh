#!/usr/bin/env bash

echo "Starting new subshell sourcing environment files."

while [ "$1" != "--" ] && [ "$1" != "" ]; do
  env_file="$1"
  shift
  while read -r line; do
    var="${line%%=*}"
    value="${line#*=}"
    eval 'export "'"$var"'"="'"$value"'"'
  done < <(grep -E -v '^\s*(#|$)' "${env_file}")
done

shift

if [ "$1" == "" ]; then
  "$SHELL"
else
  "$@"
fi
