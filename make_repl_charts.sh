#!/bin/bash
./statsrepl.sh && Rscript hist.r csv/replica_sets.csv charts/replica_sets.png
