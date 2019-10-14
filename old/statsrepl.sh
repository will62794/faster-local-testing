# Parse a big log file and produce CSV files for various stats.

task_id=$1
logfile="logs/$task_id"
filtered=`mktemp`

echo "Processing task: $task_id"
echo "Filtering logs upfront."
grep "ReplSetTest" $logfile > $filtered

echo "Producing startSet metrics."
grep "ReplSetTest.*startSet.*took" $filtered \
| sed -E "s/\[.*:(.*)\].*took (.*)ms for (.*) nodes.*/\1,\2,\3/" | sort > ${logfile}_startSet.csv

echo "Producing stopSetConsistencyChecks metrics."
grep "ReplSetTest.*stopSet data consistency.*took" $filtered \
| sed -E "s/\[.*:(.*)\].*took (.*)ms for (.*) nodes.*/\1,\2,\3/" | sort > ${logfile}_stopSetConsistencyChecks.csv 

echo "Producing stopSetShutdown metrics."
grep "ReplSetTest.*stopSet stopped.*took" $filtered \
| sed -E "s/\[.*:(.*)\].*took (.*)ms for (.*) nodes.*/\1,\2,\3/" | sort > ${logfile}_stopSetShutdown.csv 

echo "Producing initiateWithNodeZeroAsPrimary metrics."
grep "ReplSetTest.*initiateWithNodeZeroAsPrimary.*took" $filtered \
| sed -E "s/\[.*:(.*)\].*took (.*)ms for (.*) nodes.*/\1,\2,\3/" | sort > ${logfile}_initiateWithNodeZeroAsPrimary.csv