#!/bin/bash

set -e

source ./toimivuus/env/bin/activate
export $(cat .env | xargs) && python ./toimivuus/hfp_import.py \
  --first_datehour 2021-11-21T06 \
  --last_datehour 2021-11-21T12 \
  --events ARR ARS DEP PDE VJA VJOUT DA DOUT DOO DOC \
  --routes 1054 2553 2553K 4555 1010 \
  --loglvl INFO