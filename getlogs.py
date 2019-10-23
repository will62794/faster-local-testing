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

def get_log(url):
    return requests.get(url).text

def check_task(task_id):
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
    f = open(out_file, "w")
    for url in job_log_urls:
        print "Downloading log file: " + url
        text = urllib2.urlopen(url).read()
        f.write(text)
    f.close()

if __name__ == "__main__":
    # Must provide Evergreen credentials via command line.
    API_USER = sys.argv[1]
    API_KEY = sys.argv[2]
    task = sys.argv[3]
    check_task(task)
