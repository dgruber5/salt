'''
Configuration disposable regularly scheduled tasks for at.
==========================================================

The at state can be add disposable regularly scheduled tasks for your system.
'''
# Import python libs
import re
import time
import datetime

# Import salt libs
import salt.utils

# Tested on OpenBSD 5.0
BSD = ('OpenBSD', 'FreeBSD')

def __virtual__():
    '''
    Most everything has the ability to support at(1)
    '''
    if salt.utils.is_windows() or not salt.utils.which('at'):
        return False
    return 'at'


def present(job, timespec, tag=None, runas=None):

    '''
    Add a job to queue.

    job
        Command to run.

    timespec
        The 'timespec' follows the format documented in the at(1) manpage.

    tag
        Make a tag for the job.

    runas
        Users run the job.

    .. code-block:: yaml
        rose:
            at.present:
                - job: 'echo "I love you" > love'
                - timespec: '9:9 11/09/13'
                - tag: love
                - runas: jam

    '''
    ret = {'name': job,
           'changes': {},
           'result': True,
           'comment': 'job {0} is add and will run on {1}'.format(job, timespec)}

    binary = salt.utils.which('at')

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'job {0} is add and will run on {1}'.format(job, timespec)
        return ret

    if __grains__['os_family'] == 'RedHat':
        echo_cmd = 'echo -e'
    else:
        echo_cmd = 'echo'

    if tag:
        cmd = '{0} "### SALT: {4}\n{1}" | {2} {3}'.format(echo_cmd,
            job, binary, timespec, tag)
    else:
        cmd = '{0} "{1}" | {2} {3}'.format(echo_cmd, job, binary, timespec)

    if runas:
        luser = __salt__['user.info'](runas)
        if not luser:
            ret['comment'] = 'User: {0} is not exists'.format(runas)
            ret['result'] = False
            return ret
        ret['comment'] = __salt__['cmd.run']('{0}'.format(cmd), runas=runas)
    else:
        ret['comment'] = __salt__['cmd.run']('{0}'.format(cmd))

    return ret

def absent(limit, jobid=None, **kwargs):
    '''
    Remove a job from queue
    The 'kwargs' can include hour. minute. day. month. year

    limit
        Target range

    tag
        Job's tag

    runas
        Runs user-specified jobs

    .. code-block:: yaml
        revoke:
            at.absent:
                - limit: all

            at.absent:
                - limit: all
                - year: 13

            at.absent:
                - limit: all
                - tag: rose
                - runas: jim

            at.absent:
                - limit: all
                - tag: rose
                - day: 13
                - hour: 16
    '''

    ret = {'name': 'remove job',
           'changes': {},
           'result': True,
           'comment': ''}

    binary = salt.utils.which('at')
    
    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Remove jobs()'
        return ret

    if limit != 'all':
        ret['comment'] = 'limit parameter not supported {0}'.format(limit)
        ret['result'] = False
        return ret

    if jobid:
        output = __salt__['cmd.run']('{0} -d {1}'.format(binary, jobid))
        if i in map(str, [j['job'] for j in __salt__['at.atq']()['jobs']]):
            ret['result'] = False
            return ret
        ret['comment'] = 'Remove job({0}) from queue'.format(' '.join(opts))
        return ret

    if kwargs:
        opts = map(str, [j['job'] for j in __salt__['at.jobcheck'](**kwargs)['jobs']])
    else:
        opts = map(str, [j['job'] for j in __salt__['at.atq']()['jobs']])

    if not opts:
        ret['result'] = False
        ret['comment'] = 'No match jobs'
        return ret

    output = __salt__['cmd.run']('{0} -d {1}'.format(binary, ' '.join(opts)))
    fail = []
    for i in opts:
        if i in map(str, [j['job'] for j in __salt__['at.atq']()['jobs']]):
            fail.append(i)

    if fail:
       ret['comment'] = 'Remove job({0}) from queue but ({1}) fail'.format(' '.join(opts),fail)
    else:
       ret['comment'] = 'Remove job({0}) from queue'.format(' '.join(opts))

    return ret
