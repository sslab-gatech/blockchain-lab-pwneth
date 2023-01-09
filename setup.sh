#!/usr/bin/env sh

ROOT=$(realpath $(dirname "$0"))
cd $ROOT

which geth &>/dev/null || echo "[!] Install 'geth' first"

DATADIR="$ROOT/geth-data"
if [ ! -e $DATADIR ]; then
    geth init --datadir $DATADIR $ROOT/genesis.json
fi

pip3 install -r $ROOT/requirements.txt
