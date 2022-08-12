#!/bin/bash


source config.sh

mkdir -p ${DATARESULTS}/reports_short_svo
rm -f ${DATARESULTS}/reports_short_svo/*

python3 -m workers.semanticworker3 ${REPORTS_SHORT_TEXTS} ${DATARESULTS}/reports_short_svo
