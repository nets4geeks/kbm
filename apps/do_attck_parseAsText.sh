#!/bin/bash


source config.sh

mkdir -p ${ATTCK_TEXTS_TECH}
mkdir -p ${ATTCK_TEXTS_SUBTECH}
rm -f ${ATTCK_TEXTS_TECH}/*
rm -f ${ATTCK_TEXTS_SUBTECH}/*

python3 -m parsers.attckparser ${ATTCK_FILE} ${ATTCK_TEXTS_TECH} ${ATTCK_TEXTS_SUBTECH}
