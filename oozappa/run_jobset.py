# -*- coding:utf8 -*-
from datetime import datetime
from records import get_db_session, Jobset, ExecuteLog

def run_jobset(jobset_id, communicator, cli=False):
    session = get_db_session()
    jobset = session.query(Jobset).get(jobset_id)
    if jobset.cli_only and not cli:
        communicator.write(
            u"""[Oozappa:Can't do it from webui] Jobset: {0}.""".format(
                jobset.title).encode('utf8'))
        return
    executelog = ExecuteLog()
    executelog.jobset = jobset
    executelog.logfile = communicator.logfile
    session.add(executelog)
    session.commit()
    communicator.controll(exec_fabric.PROGRESS_BEGIN)
    for job in jobset.jobs:
        with exec_fabric(job.environment.execute_path) as executor:
            if executor.doit(job.tasks.split(' '), communicator) != 0:
                executelog.success = False
                executelog.finished = datetime.now()
                session.commit()
                communicator.write('\n&nbsp;\n&nbsp;\n')
                communicator.write('=' * 35 + '\n')
                communicator.write(
                    u'[Oozappa:FAILES] Jobset: {0} in {1} seconds.'.format(
                        jobset.title, executelog.execute_time()
                                      ).encode('utf8'))
                communicator.write('\n' + ('=' * 35))
                communicator.write('\n&nbsp;\n&nbsp;\n')
                communicator.controll(exec_fabric.EXEC_FAILED)
                break
    else:
        executelog.success = True
        executelog.finished = datetime.now()
        session.commit()
        communicator.write('\n&nbsp;\n&nbsp;\n')
        communicator.write('=' * 35)
        communicator.write('\n')
        communicator.write(
            u'[Oozappa:FINISHED] Jobset: {0} in {1} seconds.'.format(
                jobset.title, executelog.execute_time()
                           ).encode('utf8'))
        communicator.write('\n')
        communicator.write('=' * 35)
        communicator.write('\n&nbsp;\n&nbsp;\n')
        communicator.controll(exec_fabric.EXEC_SUCESSFUL)