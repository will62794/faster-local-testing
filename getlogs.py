#
# Fetch log URLs for all logs of a given Evergreen task.
#

import requests
import time
import argparse
import sys
import pprint
import urllib2
import os
import time
from dateutil.parser import parse as dateutil_parse

# MongoDB 'master' branch project identifier in Evergreen.
MONGO_PROJECT = "mongodb-mongo-master"

# The Evergreen REST API endpoint.
API_URL = "https://evergreen.mongodb.com/rest/v2"
API_URL_V1 = "https://evergreen.mongodb.com/rest/v1"

# You can figure these out from the Evergreen UI.
API_USER = "" # must be set via command line.
API_KEY = "" # must be set via command line.

# For authentication.
def header():
    return {"Api-User": API_USER, "Api-Key": API_KEY}

def get_tests(task_id, limit):
    url_task_tests = API_URL + "/tasks/" + task_id + "/tests"
    r = requests.get(url=url_task_tests, params={"limit": limit}, headers=header())
    return r.json()

def get_task(task_id):
    url_task = API_URL_V1 + "/tasks/" + task_id
    r = requests.get(url=url_task, headers=header())
    return r.json()

def get_task_v2(task_id):
    url_task = API_URL + "/tasks/" + task_id
    r = requests.get(url=url_task, headers=header())
    return r.json()

def get_recent_versions(n):
    url_versions = API_URL + "/projects/mongodb-mongo-master/recent_versions"
    r = requests.get(url=url_versions, params={"limit": n}, headers=header())
    return r.json()

def get_builds_for_version(versionid):
    url_versions = API_URL + "/versions/" + versionid + "/builds"
    r = requests.get(url=url_versions, params={"limit": 100}, headers=header())
    return r.json() 

def get_tasks_for_build(buildid):
    url_tasks = API_URL + "/builds/" + build_id + "/tasks"
    r = requests.get(url=url_tasks, params={"limit": 100}, headers=header())
    return r.json()

def get_log(url):
    return requests.get(url).text

def save_test_durations(tests, file_prefix):
    """ Extract and save the execution times for each test in the given set. """
    durations = []
    for t in tests:
        test_name = t['test_file'].split("/")[-1].split(".")[0]
        startt = float(dateutil_parse(t['start_time']).strftime('%s.%f'))
        endt = float(dateutil_parse(t['end_time']).strftime('%s.%f'))
        duration_ms = (endt-startt)*1000
        duration = [test_name, duration_ms]
        durations.append(duration)

    out_file = file_prefix + ",durations"
    f = open(out_file, "w")
    for d in durations:
        row = ",".join([str(el) for el in d])
        f.write(row + "\n")
    return durations

def check_task(task_id, durations_only):
    """ Get all log files for a given task id. """
    task = get_task(task_id)
    logs_dir = "logs"

    patch_id = "none" if ("patch_id" not in task) else task["patch_id"]

    print "Task Name:", task["display_name"]
    print "Task ID:", task_id
    print "Patch ID:", patch_id
    print "Revision:", task["revision"]
    print "Task Build Variant:", task["build_variant"]

    # Don't check this task if it hasn't run yet.
    if task['status'] == 'undispatched':
        print "Skipping this task, since it is undispatched.\n"
        return

    # Get all tests from this task.
    tests = get_tests(task_id, 10000)
    test_log_urls = [test['logs']['url_raw'] for test in tests]
    job_log_urls = list(
        set([u[:u.find("/test/")] + "/all?raw=1" for u in test_log_urls]))
    print str(len(tests)) + " tests for this task.", str(len(job_log_urls)) + " job log URLs."

    # Save the log files into one big file.
    out_file = logs_dir + "/" + task_id

    # Include identifying information in the log file name.
    elems = [task["build_variant"], task["display_name"], patch_id, task["revision"]]
    out_file_name = ",".join(elems)
    out_file = logs_dir + "/" + out_file_name

    # Save the total durations of tests to a separate file as well. This file will just be a CSV.
    print "Saving test durations."
    save_test_durations(tests, out_file)
    if durations_only:
        return

    f = open(out_file, "w")
    for url in job_log_urls:
        print "Downloading log file: " + url
        text = urllib2.urlopen(url).read()
        f.write(text)
    f.close()

def check_task_duration(task_id):
    task = get_task_v2(task_id)
    task_log_url = task["logs"]["task_log"] + "&text=true"
    r = requests.get(url=task_log_url, headers=header())
    lines = r.text.split("\n")
    lines  = filter(lambda l : "passed in" in l, lines)
    for l in lines:
        print l

def suite_duration_test():
    recent_versions = get_recent_versions(10)["versions"]
    print recent_versions
    for v in recent_versions:
        versionid = v["versions"][0]["version_id"]
        print v.keys()
        builds = get_builds_for_version(versionid)
        for b in builds:
            # print b.keys()
            if b["build_variant"] == "enterprise-rhel-62-64-bit":
                buildid = b["build_variant"] + "_"
                print b["version"]
                for t in [tsk for tsk in b["tasks"] if "replica_sets_" in tsk]:
                    print t

if __name__ == "__main__":
    # Must provide Evergreen credentials via command line.
    API_USER = sys.argv[1]
    API_KEY = sys.argv[2]
    task = sys.argv[3]
    durations_only = False
    if len(sys.argv) > 4:
        durations_only = (sys.argv[4] == "durations")
    
    # Create output directory if it doesn't exist.
    os.system("mkdir -p logs")
    
    check_task(task, durations_only)

    # suite_duration_test()


        


