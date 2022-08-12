#!/bin/bash


source config.sh

mkdir -p ${DATARESULTS}/semantics_compare_shorts2
rm -f ${DATARESULTS}/semantics_compare_shorts2/*


python3 -m workers.semanticompareworker2 ../extra/attck_svo_common ${DATARESULTS}/reports_short_svo ${DATARESULTS}/semantics_compare_shorts2
