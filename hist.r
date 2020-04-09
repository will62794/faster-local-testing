#
# Generate histograms from ReplSetTest, ShardingTest execution time data.
#

library("ggplot2")
library("stringr")

histplot <- function(data, title, xmax, ymax, binwdth) {
     med <- round(median(data$duration))
     pct75 <- round(quantile(data$duration, 0.75))
     pct95 <- round(quantile(data$duration, 0.95))
     unit <- ymax / 10
     plt <- ggplot(data, aes(x=duration, fill=factor(num_nodes))) +
          geom_histogram(binwidth=binwdth, size=0.1, color="black") +
          geom_vline(aes(xintercept=median(data$duration, na.rm=T)), color="lightcoral", linetype="dashed", size=0.45, alpha=0.5) +
          geom_vline(aes(xintercept=quantile(data$duration, 0.75)), color="blue", linetype="dashed", size=0.45, alpha=0.5) +
          geom_vline(aes(xintercept=quantile(data$duration, 0.95)), color="black", linetype="dashed", size=0.45, alpha=0.5) +
             # Filter out some outliers for presentation.
          xlim(0, xmax) +  
          ggtitle(title) + 
          annotate("text", x = xmax, hjust = 1, vjust=0, y = ymax, size=3.0, color="lightcoral", label = paste("median", round(median(data$duration)),sep="=")) + 
          annotate("text", x = xmax, hjust = 1, vjust=0, y = ymax - (unit*1), size=3.0, color="blue", label = paste("75th pct", round(quantile(data$duration, 0.75)),sep="=")) + 
          annotate("text", x = xmax, hjust = 1, vjust=0, y = ymax - (unit*2), size=3.0, label = paste("95th pct", round(quantile(data$duration, 0.95)),sep="=")) + 
          # Add annotations to each facet.
          #facet_grid(vars(build_variant), vars(metric), labeller = label_value, switch = "y") +
          #facet_grid(vars(revision), vars(metric), labeller = label_value, switch = "y") +
          # Move axis ticks to the right. 
          scale_y_continuous("count", position="right") + 
          ylim(0, ymax) + 
          #scale_x_continuous(breaks = round(seq(0, max(10000), by = 500),1)) +
          theme(strip.text.y = element_text(size = 8, angle = 180))
     return(plt)
}

# Read commmand line args.
args = commandArgs(trailingOnly=TRUE)

# file <- "/Users/williamschultz/Dropbox/MongoDB/Replication/Projects/Faster Local Testing/csv/replica_sets.csv"
file <- args[1]
outfile <- args[2]
repl <- read.table(file, header=TRUE, sep=",")

# Create histograms for each unique (patch_id, build_variant, display_name, revision, metric) combination.
# There's probably a better way to do this without a for loop but that's works for now.
combos <- unique(repl[,c("patch_id","build_variant","display_name","revision","metric")])
for(row in 1:nrow(combos)){
     patch_id <- combos[row,"patch_id"]
     build_variant <- combos[row,"build_variant"]
     display_name <- combos[row,"display_name"]
     revision <- combos[row,"revision"]
     metric <- combos[row,"metric"]

     isRollbackMetric <- grepl("RollbackTest", metric)

     # Select the subset of data we want.
     replsub <- repl[repl$patch_id == combos[row,"patch_id"] & repl$build_variant == combos[row,"build_variant"] & repl$display_name == combos[row,"display_name"] & repl$revision == combos[row,"revision"]& repl$metric == combos[row,"metric"],]
     # For sharding tests, use a larger scale.
     xmax <- if(metric == "totalDuration") 100000 
               else if(is.element("stopShards", factor(repl$metric))) 20000
               # For RollbackTest measurements tests, use a smaller scale.
               else if(isRollbackMetric) 2000
               else 10000
     ymax <- if(metric == "totalDuration") 50 else if(isRollbackMetric) 20 else 300
     binwidth <- if(isRollbackMetric) 50 else 100
     subplt <- histplot(replsub, metric, xmax, ymax, binwidth)

     # Save the plot.
     ident <- paste(patch_id, build_variant, revision, metric,sep =",")
     filepath <- paste("charts/", display_name, "/", ident, ".png", sep="")
     print(paste("Saving plot."))
     print(paste("Path:", filepath))
     print(paste("Rows:", nrow(replsub)))
     print(paste("Metric:", metric))
     print("----------------")
     ggsave(filepath, plot=subplt, device="png", width=12, height=3)
}


# Create histogram plot for all data.
#plt <- histplot(repl)

# Save the plot.
# Scale height appropriately.
#h <- length(unique(repl$build_variant)) * 2.25 
#ggsave(outfile, plot=plt, device="png", width=16, height =h)