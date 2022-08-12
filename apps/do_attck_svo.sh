#!/bin/bash


source config.sh

mkdir -p ${DATARESULTS}/attck_semantics
rm -f ${DATARESULTS}/attck_semantics/*


python3 -m workers.semanticworker3 ${ATTCK_TEXTS_TECH} ${DATARESULTS}/attck_semantics
#python3 -m workers.semanticworker ${TEST_S} ${DATARESULTS}/attck_semantics
