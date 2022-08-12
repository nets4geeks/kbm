#!/bin/bash


source config.sh

mkdir -p ${DATARESULTS}/semantics_compare_shorts
rm -f ${DATARESULTS}/semantics_compare_shorts/*


python3 -m workers.semanticompareworker2 ${ATTCK_SVO} ${DATARESULTS}/reports_short_svo ${DATARESULTS}/semantics_compare_shorts
