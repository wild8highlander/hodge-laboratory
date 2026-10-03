#!/usr/bin/env bash
# The polyglot propagation check (v1.8): the C kernel against the
# frozen expected values.  Bit-identical or FAIL.
set -e
cd "$(dirname "$0")/c"
cc -O2 -o verhodge_kernel verhodge_kernel.c
./verhodge_kernel
