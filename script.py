from jenkinsapi.jenkins import Jenkins
from datetime import datetime
import sqlite3

# Jenkins Login details
jenkins_url = 'http://localhost:9090/'
username = 'JenkinsDroplet'
password = 'JenkinsDroplet404'
db_name = 'jenkinsDB.db'


# server instance
server = Jenkins(jenkins_url, username, password)
print(server.get_jobs())

# Initiate Database
db_connect = sqlite3.connect(db_name)
db_cursor = db_connect.cursor()



for job_name, job_instance in server.get_jobs():
    job_name = server.get_job(job_instance.name)
    if job_instance.is_running():
        job_status = 'RUNNING'
    elif job_instance.get_last_build_or_none() == None:
        job_status = 'NOTBUILT'
    else:
        job_name = server.get_job(job_instance.name)
        last_build = job_name.get_last_build()
        job_status = last_build.get_status()
    todays_date = datetime.now()
    checked_time = todays_date.strftime("%Y-%m-%d %H:%M:%S")

    try:
        db_cursor.execute("CREATE TABLE jobs (job_name, job_status, checked_time)")
    except sqlite3.OperationalError:
        # table created already, so just pass
        pass

    db_cursor.execute('SELECT job_name FROM jobs WHERE job_name="{job_name}"'.format(job_name=job_name))
    data_name = db_cursor.fetchone()
    # print(data_name)

    if data_name is None:
        query = ("INSERT INTO jobs VALUES ('{job_name}', '{job_status}', '{checked_time}')"
                 .format(job_name=job_name, job_status=job_status, checked_time=checked_time))
        db_cursor.execute(query)
    else:
        db_cursor.execute('UPDATE jobs SET job_status="{job_status}", checked_time="{checked_time}" WHERE job_name="{job_name}"'
                          .format(job_status=job_status, checked_time=checked_time, job_name=job_name))

    db_connect.commit()
    # print(job_status, job_name, checked_time)


def list_db_jobs():
    db_cursor.execute("SELECT * FROM jobs")
    result = db_cursor.fetchall()
    for x in result:
        print(x)
list_db_jobs()
db_connect.close()




