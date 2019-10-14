# Download each log file.
echo "" > all_logs.txt
for url in `cat urls.txt`; 
	do curl "$url" >> all_logs.txt
done
