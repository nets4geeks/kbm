#!/bin/bash

DATA=../data
DATASOURCES=${DATA}/sources
DATASETS=${DATA}/sets
DATARESULTS=${DATA}/results

EXTRA=../extra

ATTCK_URL=https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json
ATTCK_FILE=${DATASOURCES}/enterprise-attack.json
ATTCK_TEXTS_TECH=${DATASETS}/attck_texts_tech
ATTCK_TEXTS_SUBTECH=${DATASETS}/attck_texts_subtech
ATTCK_SVO=${EXTRA}/attck_svo
ATTCK_SIMPLE_TECH=${EXTRA}/attck_simple

CWE_URL=https://cwe.mitre.org/data/xml/cwec_latest.xml.zip
CWE_ARCH=${DATASOURCES}/cwec_latest.xml.zip
CWE_FILE=${DATASOURCES}/cwec_v4.6.xml
CWE_TEXTS=${DATASETS}/cwe_texts

POS=pos_dataset
POS_SRC=${EXTRA}/${POS}/source.txt
POS_RAW=${EXTRA}/${POS}/raw.txt
POS_TRUE=${EXTRA}/${POS}/truth.txt

REPORTS_SHORT_TEXTS=${EXTRA}/reports_short
