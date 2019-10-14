# Parse a big log file and produce CSV files for various stats.

task_id=$1
logfile="logs/$task_id"
filtered=`mktemp`

echo "Filtering logs upfront."
grep "ShardingTest" $logfile > $filtered

echo "Producing startupAndInitiate metrics."
grep "ShardingTest startup and initiation for all shards.*took" $filtered \
| sed -E "s/\[.*:(.*)\].*took (.*)ms for (.*) shards.*/\1,\2,\3/" | sort > ${logfile}_startupAndInitiate.csv

echo "Producing startupAndInitiateConfigServer metrics."
grep "ShardingTest startup and initiation for the config server.*took" $filtered \
| sed -E "s/\[.*:(.*)\].*took (.*)ms with (.*) nodes.*/\1,\2,\3/" | sort > ${logfile}_startupAndInitiateConfigServer.csv

echo "Producing stopShards metrics."
grep "ShardingTest stopped all.*took" $filtered \
| sed -E "s/\[.*:(.*)\].*took (.*)ms.*/\1,\2,0/" | sort > ${logfile}_stopShards.csv 
