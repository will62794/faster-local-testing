#
# Process all log files for different tasks and produce one CSV where each row describes a test execution
# and its duration, along with some other info.
#

logdir="logs"
csv="csv/sharding.csv"

# Create CSV columns.
echo "build_variant,display_name,patch_id,revision,test_name,metric,duration,num_nodes" > $csv

for i in `ls ${logdir} | grep -v "csv" | grep -v ",durations" | grep "sharding"`; do  
echo "Processing $i"
# We also add the metadata columns which are contained in the filename.
grep "ShardingTest.*took" $logdir/$i \
| sed -E -e "s/\[.*:(.*)\].*startup and initiation for all nodes.*took (.*)ms with (.*) config server nodes and (.*) total shard nodes/$i,\1,startupAndInitiate,\2,\4/" \
         -e "s/\[.*:(.*)\].*startup for all nodes took (.*)ms with (.*) config server nodes and (.*) total shard nodes/$i,\1,startShardsAndConfigServer,\2,\4/" \
         -e "s/\[.*:(.*)\].*stopped all.*took (.*)ms for (.*) shards.*/$i,\1,stopShards,\2,\3/" \
         | grep -v "js_test:" >> $csv # remove any unprocessed lines.
done

# Handle 'durations' logs.
for i in `ls ${logdir} | grep ",durations" | grep "sharding"`; do  
# echo "Processing $i"
# We also add the metadata columns which are contained in the filename.
meta=`echo $i | cut -d "," -f1-4`
echo "Processing test durations for $meta"
cat logs/$i \
| sed -E -e "s/(.*),(.*)/$meta,\1,totalDuration,\2,0/" \
         | grep -v "js_test:" >> $csv # remove any unprocessed lines.
done
