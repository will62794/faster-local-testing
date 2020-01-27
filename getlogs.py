"""
Fetch logs of a given Evergreen patch/version build, or one task within a build.
"""

import argparse
import os
import re
import tempfile

import requests
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

def _get_resource(resource_type, resource_id):
    # Note the "s": we get a version from "/versions/".
    url = API_URL_V1 + "/" + resource_type + "s/" + resource_id
    r = requests.get(url=url, headers=header())
    return r.json()

def get_version(version_id):
    return _get_resource('version', version_id)

def get_build(build_id):
    return _get_resource('build', build_id)

def get_task(task_id):
    return _get_resource('task', task_id)

def get_tests(task_id, limit):
    url_task_tests = API_URL + "/tasks/" + task_id + "/tests"
    r = requests.get(url=url_task_tests, params={"limit": limit},
                     headers=header())
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

def download_file(url, filename):
    with tempfile.NamedTemporaryFile() as tmp:
        for command in [
            'curl -L %s -O %s' % (url, tmp.name),
            'cat %s > %s' % (tmp.name, filename)
        ]:
            print command
            retval = os.system(command)
            if retval != 0:
                raise Exception('returned %d' % retval)

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
    if type(tests) == dict and tests.get('status') != 200:
        print 'Error', tests['status'], tests.get('error')
        return

    test_log_urls = [test['logs']['url_raw'] for test in tests]
    job_log_urls = list(
        set([u[:u.find("/test/")] + "/all?raw=1" for u in test_log_urls]))
    print str(len(tests)) + " tests for this task.", str(len(job_log_urls)) + " job log URLs."

    # Save the log files into one big file.
    # Include identifying information in the log file name.
    elems = [task["build_variant"], task["display_name"], patch_id, task["revision"]]
    out_file_name = ",".join(elems)
    out_file = logs_dir + "/" + out_file_name

    # Save the total durations of tests to a separate file as well. This file will just be a CSV.
    print "Saving test durations."
    save_test_durations(tests, out_file)
    if durations_only:
        return

    for url in job_log_urls:
        print "Downloading log file: " + url
        max_tries = 10
        while True:
            try:
                download_file(url, out_file)
                break
            except Exception as exc:
                if max_tries:
                    print repr(exc), "Retrying..."
                    max_tries -= 1
                else:
                    print repr(exc), "Giving up"
                    break

def check_version(version_id, durations_only, task_pattern):
    version = get_version(version_id)

    print "Version ID:", version_id
    print len(version['builds']), "builds"

    builds = [get_build(build_id) for build_id in version['builds']]
    tasks = [task for build in builds for task in build['tasks'].values()]
    print len(tasks), "tasks"

    for i, task in enumerate(tasks):
        task_id = task['task_id']
        if task['status'] == 'failed':
            continue

        if task_pattern and not task_pattern.match(task_id):
            continue

        print "Task ID: %s, %d of %d" % (task_id, i, len(tasks))
        check_task(task_id, durations_only)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('API_USER',
                        help='Evergreen username',
                        nargs=1)
    parser.add_argument('API_KEY',
                        help='Evergreen API key',
                        nargs=1)
    parser.add_argument('--task',
                        help='Evergreen task ID')
    parser.add_argument('--task-pattern',
                        help='Python regex to match task names within a build',
                        type=re.compile)
    parser.add_argument('--version',
                        help='Evergreen version ID or patch ID')
    parser.add_argument('--durations-only',
                        help='Measure durations without fetching logs',
                        action='store_true')

    args = parser.parse_args()

    API_USER = args.API_USER[0]
    API_KEY = args.API_KEY[0]
    if not args.task and not args.version:
        parser.error('Must supply --task or --version')
    elif args.task and args.version:
        parser.error('Cannot supply both --task and --version')
    elif args.task_pattern and not args.version:
        parser.error('Cannot supply both --task and task-pattern')

    # Create output directory if it doesn't exist.
    os.system("mkdir -p logs")

    if args.task:
        check_task(args.task, args.durations_only)
    else:
        check_version(args.version, args.durations_only, args.task_pattern)
