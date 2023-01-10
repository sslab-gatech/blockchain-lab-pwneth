#!/usr/bin/env sh

ROOT=$(realpath $(dirname "$0"))
cd $ROOT

DATADIR="$ROOT/geth-data"

geth --datadir="$DATADIR" attach
