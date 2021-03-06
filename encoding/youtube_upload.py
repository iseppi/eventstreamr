#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import os
import fnmatch
import time

from lib.schedule import *

config_file = 'config.json'
config_data = open_json(config_file)

base_dir = config_data['base_dir']
queue_todo_dir = os.path.join(base_dir, 'completed')
queue_wip_dir = os.path.join(base_dir, 'uploading')
queue_done_dir = os.path.join(base_dir, 'uploaded')
youtube_log_file = os.path.join(base_dir, 'youtube_uploads.log')
schedule_file = os.path.join(base_dir, config_data['schedule'])
json_format="%Y-%m-%d %H:%M:%S"

email_address = 'username'
password = 'password'

schedule = get_schedule(schedule_file, json_format)
schedule = { t['schedule_id']: t for t in schedule  }

def move_job(src_dir, dst_dir, jobname):
    files = os.listdir(src_dir)
    for filename in files:
        if fnmatch.fnmatch(filename, jobname + '.[lm][op][g4]'):
            src = os.path.join(src_dir, filename)
            dst = os.path.join(dst_dir, filename)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            os.rename(src, dst)

while True:
    files = os.listdir(queue_todo_dir)
    if len(files):
        filename = files[0]
        if fnmatch.fnmatch(filename, '*.mp4'):
            job = filename[:-4]
            print "Starting job " + job
            move_job(queue_todo_dir, queue_wip_dir, job)

            upload_file = os.path.join(queue_wip_dir, filename)
            title = schedule[int(job)]['title']
            abstract = schedule[int(job)]['abstract']
            presenters = schedule[int(job)]['presenters']
            description = abstract + ' by ' + presenters
            args = ['youtube_upload', '--email=' + email_address, '--password=' + password, '--unlisted', '--title=' + title, '--category=Tech', '--description=' + description, upload_file]

            log_file = os.path.join(queue_wip_dir, job + '.log')
            with open(youtube_log_file, 'a') as youtube_log, open(log_file, 'w') as log:
                process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdoutdata, stderrdata) = process.communicate()
                if stdoutdata:
                    youtube_log.write("\t".join([job, stdoutdata.strip(), title]) + "\n")
                if stderrdata:
                    log.write(stderrdata)
            print "Finished job " + job
            move_job(queue_wip_dir, queue_done_dir, job)
    else:
        print "Nothing to do, sleeping"
        time.sleep(10)
