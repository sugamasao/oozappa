# -*- coding:utf8 -*-
import os
from fabric.main import load_fabfile
from fabric.contrib.files import upload_template as fabric_upload_template

class FabricTask(object):
    def __init__(self, task_dict):
        self._task_dict = task_dict
    def name(self):
        return self._task_dict.name
    @property
    def description(self):
        return self._task_dict.__doc__ or u''
    def __str__(self):
        return self.name()
    def __repr__(self):
        return self.__str__()

class FabricHelper(object):
    def __init__(self, path):
        _path = path
        if not path.endswith('fabric'):
            _path = os.path.join(path, 'fabfile')
        _dict = load_fabfile(_path)[1]
        self.task_dict = dict((x.name, FabricTask(x)) for x in _dict.values())
        self.directory = os.path.split(path)[0]

    def task_list(self):
        return self.task_dict
    def task(self, name):
        return self.task_dict[name]

def print_task_list(path):
    tasks = load_fabfile(path)
    task_dict = tasks[1]
    for task in task_dict.values():
        print(u'{0:10}: {1}'.format(task.name, task.__doc__))

TEMPLATES_DIRNAME = 'templates'

def upload_template(filename, destination, context=None,
    template_dir=None, use_sudo=False, backup=True, mirror_local_mode=False,
    mode=None):
    '''Search filename in ENVIRONMENT_DIR/templates at first and then common/templates if template_dir is not supplied.
      Call fabric.contrib.file.upload_template passing directory that is found filename, or None.
      if template_dir passed, this function just call fabric.contrib.file.upload_template as usual.

      *) use_jinja option is always True and you can't pass use_jinja option to this function.
    '''
    _template_dir = template_dir
    if not _template_dir:
        call_path = os.getcwd()
        common_path = os.path.abspath(os.path.join(call_path, '..', 'common'))
        if os.path.exists( os.path.join(call_path, TEMPLATES_DIRNAME, filename)):
            print('found called path')
            _template_dir = os.path.join(call_path, TEMPLATES_DIRNAME)
        elif os.path.exists( os.path.join(common_path, TEMPLATES_DIRNAME, filename)):
            print('found common path')
            _template_dir = os.path.join(common_path, TEMPLATES_DIRNAME)
        else:
            print('NOT FOUND {0}'.format(os.path.join(call_path, TEMPLATES_DIRNAME, filename)))
            print('NOT FOUND {0}'.format(os.path.join(common_path, TEMPLATES_DIRNAME, filename)))
    return fabric_upload_template(filename, destination, context=context, use_jinja=True,
        template_dir=_template_dir, use_sudo=use_sudo, backup=backup, mirror_local_mode=mirror_local_mode,
        mode=mode)



