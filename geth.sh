#!/usr/bin/env bash

geth --datadir=./geth-data --networkid=1337 --syncmode=full --gcmode=archive --http --http.corsdomain="*" --http.api=web3,eth,debug,personal,net --allow-insecure-unlock --bootnodes=enode://d6686e0acb89f5b42d325aaad6a77f6d2c4fe9d2966a45e153ed50051e7617ee22e027ec78e600a2720482399ab74375e97287d357e9f1e4bea473a44c4842ec@iron.gtisc.gatech.edu:30303 --ethstats "student-node-$RANDOM:THIS_SECRET_DOESNT_MATTER_NOT_EXPOSED@iron.gtisc.gatech.edu:3000" "$@"
