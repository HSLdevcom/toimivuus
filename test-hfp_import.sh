#!/bin/bash

set -e

source ./toimivuus/env/bin/activate
export $(cat .env | xargs) && python ./toimivuus/hfp_import.py --datehours 2021-11-21T06 2021-11-21T07 \
  --events ARS ARR PDE DEP \
  --routes 1054 2553 2553K 4555 1010