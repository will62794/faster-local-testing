#!/bin/sh

# Generate CSV duration data from each log for replica sets and sharding suites.
for i in `ls logs | grep -v "csv" | grep "replica_sets"`; do ./statsrepl.sh $i; done
for i in `ls logs | grep -v "csv" | grep "sharding"`; do ./statssharding.sh $i; done

# Generate histogram charts for all logs.
python hist.py `ls logs | grep -v "csv" | grep "replica_sets" | paste -s -d, -` startSet,initiateWithNodeZeroAsPrimary,stopSetShutdown,stopSetConsistencyChecks "charts/durations_replica_sets.svg"
python hist.py `ls logs | grep -v "csv" | grep "sharding" | paste -s -d, -` startupAndInitiate,startupAndInitiateConfigServer,stopShards "charts/durations_sharding.svg"
