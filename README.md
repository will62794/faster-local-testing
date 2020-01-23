## Faster Local Testing Scripts

This repository houses scripts to help analyze the performance of MongoDB Javascript integration tests, specifically those that utilize the `ReplSetTest` or `ShardingTest` fixture. To download logs from a given Evergreen task, run the following:

```
python getlogs.py  <API_USER> <API_KEY> --task <TASK_ID>
```

This will download all the logs for tests run in that task and save them into a single file inside a `logs` directory. Each log file is named as a comma-separated tuple that includes identifying information about where the log came from e.g.

```
build_variant,test_suite,patch_id,revision
```

To extract metrics from all the downloaded log files, for *sharding* and *replica_sets* suites you can run

```
./statsrepl.sh
./statsharding.sh
```
which processes all files in the `logs` directory and outputs a CSV file in the `csv` directory, named `csv/replica_sets.csv` or `csv/sharding.csv`, respectively. Finally, to generate charts visualizing the extracted metrics for *sharding* or *replica_sets* suites, you can run

```
Rscript hist.r csv/replica_sets.csv csv/replica_sets_summary.csv
Rscript hist.r csv/sharding.csv csv/sharding_summary.csv
```

which should produce PNG charts inside the `charts` directory. The charts are generated using R and ggplot2, so you should have those installed, which you should be able to test by running `Rscript` from the command line. 

After downloading the appropriate logs, you can more easily run the metric extraction and chart generation in a single step by running:

```
./make_repl_charts.sh
./make_sharding_charts.sh
```
