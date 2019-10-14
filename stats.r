#
# Compute aggregate statistics about ReplSetTest and ShardingTest datasets.
#

library(dplyr)

# Read commmand line args.
args = commandArgs(trailingOnly=TRUE)

file <- args[1]
outfile <- args[2]
repl <- read.table(file, header=TRUE, sep=",")

attach(repl)
# Generate basic summary statistics.
summ <- repl %>%
        group_by(build_variant, metric) %>%
        summarize(mean=round(mean(duration),0),median=round(median(duration),0),sd=round(sd(duration))) 
detach(repl)
write.csv(summ, outfile, row.names=FALSE)

