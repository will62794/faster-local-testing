#
# Generate histograms from ReplSetTest, ShardingTest execution time data.
#

library("ggplot2")
library("stringr")

histplot <- function(data) {
     plt <- ggplot(data, aes(x=duration, fill=factor(num_nodes))) +
          geom_histogram(binwidth=100, size=0.1, color="black") +
          # Filter out some outliers for presentation.
          xlim(0, 10000) +  
          # Add annotations to each facet.
          facet_grid(vars(build_variant), vars(metric), labeller = label_value, switch = "y") +
          #facet_grid(vars(revision), vars(metric), labeller = label_value, switch = "y") +
          # Move axis ticks to the right. 
          scale_y_continuous("count", position="right") + 
          ylim(0, 300) + 
          theme(strip.text.y = element_text(size = 8, angle = 180))
     return(plt)
}

# Read commmand line args.
args = commandArgs(trailingOnly=TRUE)

# file <- "/Users/williamschultz/Dropbox/MongoDB/Replication/Projects/Faster Local Testing/csv/replica_sets.csv"
file <- args[1]
outfile <- args[2]
repl <- read.table(file, header=TRUE, sep=",")

# Create histograms for each unique (patch_id, build_variant, display_name, revision) combination.
# There's probably a better way to do this without a for loop but that's works for now.
combos <- unique(repl[,c("patch_id","build_variant","display_name","revision")])
for(row in 1:nrow(combos)){
     patch_id <- combos[row,"patch_id"]
     build_variant <- combos[row,"build_variant"]
     display_name <- combos[row,"display_name"]
     revision <- combos[row,"revision"]

     # Select the subset of data we want.
     replsub <- repl[repl$patch_id == combos[row,"patch_id"] & repl$build_variant == combos[row,"build_variant"] & repl$display_name == combos[row,"display_name"] & repl$revision == combos[row,"revision"],]
     subplt <- histplot(replsub)

     # Save the plot.
     ident <- paste(patch_id, build_variant, revision, sep =",")
     filepath <- paste("charts/", display_name, "/", ident, ".png", sep="")
     print(paste("Saving plot to:", filepath, "with", nrow(replsub), "rows."))
     ggsave(filepath, plot=subplt, device="png", width=12, height=3)
}


# Create histogram plot for all data.
plt <- histplot(repl)

# Save the plot.
# Scale height appropriately.
h <- length(unique(repl$build_variant)) * 2.25 
ggsave(outfile, plot=plt, device="png", width=16, height =h)