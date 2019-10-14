#
# Generate histograms from ReplSetTest, ShardingTest execution time data.
#

library("ggplot2")
library("stringr")

# Read commmand line args.
args = commandArgs(trailingOnly=TRUE)

# file <- "/Users/williamschultz/Dropbox/MongoDB/Replication/Projects/Faster Local Testing/csv/replica_sets.csv"
file <- args[1]
outfile <- args[2]
repl <- read.table(file, header=TRUE, sep=",")

attach(repl)
means <- aggregate(repl, by=list(build_variant), mean)
detach(repl)

# Create the plot.
ggplot(repl, aes(x=duration, fill=factor(num_nodes))) +
     geom_histogram(binwidth=100, size=0.1, color="black") +
     ylim(0, 150) + 
     # Filter out some outliers for presentation.
     xlim(0, 10000) +  
     # Add annotations to each facet.
     facet_grid(vars(build_variant), vars(metric), labeller = label_value, switch = "y") +
     # Move axis ticks to the right. 
     scale_y_continuous("count", position="right") + 
     theme(strip.text.y = element_text(size = 8, angle = 180))

# Save the plot.
# Scale height appropriately.
h <- length(unique(repl$build_variant)) * 2.25 
ggsave(outfile, device="png", width=16, height =h)