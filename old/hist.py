import matplotlib.pyplot as plt
import numpy as np
import csv
import sys

# Read each duration in CSV file.
# metrics = ["initiate", "startSet", "stopSetShutdown"]
# metrics = ["startupAndInitiate", "stopShards"]


# Take in a list of task ids.
task_ids = sys.argv[1].split(",")
# Take in a list of metrics to report.
metrics = sys.argv[2].split(",")
# Where to save the final chart
outfile = sys.argv[3]

durations = {}

for metric in metrics:
    durations[metric] = {}
    for task_id in task_ids:
        durations[metric][task_id] = {"durations": [], "numNodes": []}
        csv_file = "logs/" + task_id + "_" + metric + ".csv"
        csv_reader = csv.reader(open(csv_file), delimiter=',')
        for row in csv_reader:
            duration = int(row[1])
            durations[metric][task_id]["durations"].append(duration)
            # Include the number of nodes for this data point if it was recorded.
            if len(row)>2:
                numNodes = int(row[2])
                durations[metric][task_id]["numNodes"].append(numNodes)

w,h = (len(metrics)*7, len(task_ids)*4)
fig, axs = plt.subplots(len(task_ids), len(metrics), figsize=(w,h))

# Plot histogram for each metric and task id. We plot metrics
# for different task ids in the same column so they can be easily
# compared by eye.
for col,metric in enumerate(metrics):
    for row,task_id in enumerate(task_ids):
        # If the duration list is empty, skip it.
        if durations[metric][task_id]["durations"] == []:
            continue
        # print durations[metric][task_id]["numNodes"]
        task_durations = durations[metric][task_id]["durations"]
        # if len(durations[metric][task_id]["numNodes"]) > 0:
        #     task_durations = [durations[metric][task_id]["durations"][i] for i in range(len(durations[metric][task_id]["durations"])) if durations[metric][task_id]["numNodes"][i]==3]
        small = [w for w in task_id.split("_") if len(w)<12]
        task_suite = "_".join(small)
        ax = axs[row, col]
        
        np.histogram(task_durations)
        
        binwidth = 200
        n, bins, patches = ax.hist(x=task_durations, bins=np.arange(0, 12000, binwidth),
                                    alpha=0.8, rwidth=0.85, histtype="barstacked", stacked=True, color='gray')

        # dots_x = []
        # dots_y = []
        # colors = []
        # if len(durations[metric][task_id]["numNodes"])>0:
        #     for i,el in enumerate(task_durations):
        #         dots_x.append(task_durations[i])
        #         dots_y.append(np.random.rand()*2)
        #         color = "black"
        #         if durations[metric][task_id]["numNodes"][i]==3:
        #             color = "red"
        #         if durations[metric][task_id]["numNodes"][i]==2:
        #             color = "blue"
        #         if durations[metric][task_id]["numNodes"][i]==1:
        #             color = "green"
        #         colors.append(color)

        # ax.scatter(dots_x, dots_y, s=1, c=colors, marker="s")
        # ax.scatter(dots_x, dots_y, s=0.25, c=colors, marker="o", alpha=0.5)


        # hist, bins = np.histogram(task_durations, bins=50, range=(0,10000))
        colormap = {0: "gray", 1:"blue", 2:"green", 3:"red", 4:"orange", 5:"purple", 6:"magenta", 7:"aqua", 8:"yellow"}
        dots_x = []
        dots_y = []
        colors = []
        if len(durations[metric][task_id]["numNodes"])>0:
            for b in bins:
                # Find all durations that fall into this bin.
                bininds = [i for i in range(len(task_durations)) if (task_durations[i] >= b) and (task_durations[i] <= b + binwidth)]
                numNodeArr = [durations[metric][task_id]["numNodes"][i] for i in bininds]
                if len(numNodeArr):
                    counts = np.bincount(numNodeArr)
                    maxind = np.argmax(counts)

                for n, ind in enumerate(bininds):
                    dots_x.append(b + binwidth/2)
                    dots_y.append(n + 0.5)
                    # print durations[metric][task_id]["numNodes"][ind]
                    numnodes = durations[metric][task_id]["numNodes"][ind]
                    colors.append(colormap[numnodes])
                    
                # print sorted(numNodeArr)
        # print n, bins
        # for i in range(len(patches)):
        #     patches[i].set_facecolor("orange")

        ax.scatter(dots_x, dots_y, s=2.0, c=colors, marker="s",zorder=2, alpha=0.55, label=["red", "blue", "green"])
        # ax.legend()

            
        ax.set_xlabel('Duration (ms)')
        ax.set_ylabel('Count')
        ax.set_ylim([0,180]) # set the y limit for all plots.
        ax.set_title(metric)
        ax.set_xticks(np.arange(0, 12000, step=1000))
        # yticks(np.arange(0, 150, step=25))
        mean = np.mean(task_durations)
        median = np.median(task_durations)
        #, bbox=dict(facecolor='gray', alpha=0.25)
        ax.text(0.015, 0.85, 'Mean:%d\nMedian:%d' % (mean, median), transform=ax.transAxes, fontsize=7)
        ax.text(0.015, 0.95, task_suite, transform=ax.transAxes, fontsize=7)
        ax.grid(alpha=0.2)

        # Draw the legend using dummy lines.
        # ax.hold(True)
        colorids = sorted(colormap.keys())
        colorvals = [colormap[cid] for cid in colorids]
        dummies = [ax.plot([], [], ls='-', c=c)[0] for c in colorvals]        
        ax.legend(dummies, colorids)

# fig.suptitle(task_id, fontsize=6)
plt.tight_layout()
# plt.savefig("stats/" + task_id + ".svg")
# plt.savefig("stats/" + "durations" + ".svg")
plt.savefig(outfile)