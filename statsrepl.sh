#
# Process all log files for different tasks and produce one CSV where each row describes a test execution
# and its duration, along with some other info.
#

logdir="logs"
csv="csv/replica_sets.csv"

# Create CSV columns.
echo "build_variant,display_name,patch_id,revision,test_name,metric,duration,num_nodes" > $csv

for i in `ls ${logdir} | grep -v "csv" | grep "replica_sets"`; do  
echo "Processing $i"
# We also add the metadata columns which are contained in the filename.
grep "ReplSetTest.*took" logs/$i \
| sed -E -e "s/\[.*:(.*)\].*(startSet) took (.*)ms for (.*) nodes.*/$i,\1,\2,\3,\4/" \
         -e "s/\[.*:(.*)\].*stopSet stopped.*took (.*)ms for (.*) nodes.*/$i,\1,stopSetShutdown,\2,\3/" \
         -e "s/\[.*:(.*)\].*stopSet data consistency.*took (.*)ms for (.*) nodes.*/$i,\1,stopSetConsistencyChecks,\2,\3/" \
         -e "s/\[.*:(.*)\].*(initiateWithNodeZeroAsPrimary).*took (.*)ms for (.*) nodes.*/$i,\1,\2,\3,\4/" \
         | grep -v "js_test:" >> $csv # remove any unprocessed lines.
done
