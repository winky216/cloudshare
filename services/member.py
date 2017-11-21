import os
import glob

import core.basedata
import utils.builtin
import services.company
import services.project
import services.secret
import services.base.storage
import services.simulationacc

import sources.industry_id


class Member(services.base.storage.BaseStorage):

    commitinfo = 'Member'
    PRJ_PATH = 'projects'
    ACC_PATH = 'accounts'
    CV_PATH = 'curriculumvitaes'
    CO_PATH = 'companies'
    config_file = 'config.yaml'

    default_model = 'default'
    max_project_nums = 3

    def __init__(self, acc_repos, cv_repos,
                 mult_peo, path, name, iotype='git'):
        super(Member, self).__init__(path, name, iotype=iotype)
        self.name = name
        self.path = path
        self.cv_path = os.path.join(path, self.CV_PATH)
        self.co_path = os.path.join(path, self.CO_PATH)
        self.cv_repos = cv_repos
        self.mult_peo = mult_peo
        self.acc_repos = acc_repos
        self.projects_path = os.path.join(path, self.PRJ_PATH)
        self.accounts_path = os.path.join(path, self.ACC_PATH)
        self.companies = services.company.Company(self.co_path, name)
        self.curriculumvitaes = services.secret.Secret(
                                    services.simulationcv.SimulationCV.autoservice(
                                                            self.cv_path, name, cv_repos)
                                )
        self.config = dict()
        try:
            self.load()
        except IOError:
            pass
        if not os.path.exists(self.projects_path):
            os.makedirs(self.projects_path)

    def load(self):
        self.config = utils.builtin.load_yaml(self.path, self.config_file)

    def save(self):
        dumpconfig = utils.builtin.dump_yaml(self.config)
        self.interface.add(self.config_file, dumpconfig, message="Update config file.")

    def setup(self, config=None, committer=None):
        if config is None:
            config = {}
        modified = False
        for key in config:
            if key not in self.config or self.config[key] != config[key]:
                self.config[key] = config[key]
                modified = True
        if modified:
            self.save()
        self.load_projects()
        self.accounts = services.simulationacc.SimulationACC(self.accounts_path, self.name,
                                                             self.acc_repos)

    def use(self, id):
        result = None
        if self.accounts.exists(id):
            result = self
        return result

    def get_admins(self):
        return self.administrator

    def check_admin(self, id):
        return id in self.administrator

    def add_admin(self, inviter_id, invited_id, creator=False):
        result = False
        if creator is True or (self.check_admin(inviter_id) and
                               self.check_admin(invited_id) is False):
            self.administrator.add(invited_id)
            self.save()
            result = True
        return result

    def delete_admin(self, inviter_id, invited_id):
        result = False
        if len(self.administrator) > 1:
            if self.check_admin(inviter_id):
                if self.check_admin(invited_id):
                    self.administrator.remove(invited_id)
                    self.save()
                    result = True
        return result

    @property
    def administrator(self):
        if 'administrator' not in self.config:
            self.config['administrator'] = set()
            self.save()
        return self.config['administrator']

    def load_projects(self):
        self.projects = dict()
        for path in glob.glob(os.path.join(self.projects_path, '*')):
            if os.path.isdir(path):
                str_name = os.path.split(path)[1]
                name = unicode(str_name, 'utf-8')
                tmp_project = services.project.Project(path, self.companies,
                                                       [self.curriculumvitaes],
                                                       self.mult_peo, name)
                tmp_project.setup(config={'storageCV': self.config['storageCV'],
                                          'storagePEO': self.config['storagePEO'],
                                          'limitPEO': self.config['limitPEO']})
                tmp_project.cv_private = False
                if not tmp_project.config['autosetup'] and not tmp_project.config['autoupdate']:
                    tmp_project._modelname = self.default_model
                self.projects[name] = tmp_project

    def exists_project(self, name):
        return name in self.projects

    def add_project(self, name, classify, adminID, autosetup=False, autoupdate=False):
        result = False
        max_project_nums = self.config['max_project_nums'] if 'max_project_nums'\
                            in self.config else self.max_project_nums
        if self.check_admin(adminID) and len(self.projects) < max_project_nums:
            result = self._add_project(name, classify, autosetup=autosetup, autoupdate=autoupdate)
        return result

    def _add_project(self, name, classify, autosetup=False, autoupdate=False):
        result = False
        if len(name)>0 and name not in self.projects:
            path = os.path.join(self.projects_path, name)
            tmp_project = services.project.Project(path, self.companies, [self.curriculumvitaes],
                                                   self.mult_peo, name)
            tmp_project.setup(classify, config={'autosetup': autosetup,
                                                'autoupdate': autoupdate,
                                                'storageCV': self.config['storageCV'],
                                                'storagePEO': self.config['storagePEO'],
                                                'limitPEO': self.config['limitPEO']})
            tmp_project.cv_private = False
            tmp_project._modelname = self.default_model
            self.projects[name] = tmp_project
            result = True
        return result

    def add_account(self, inviter_id, invited_id, committer, creator=False):
        result = False
        if creator is True or self.check_admin(inviter_id):
            bsobj = core.basedata.DataObject(metadata={'id': invited_id}, data=None)
            result = self.accounts.add(bsobj, committer=committer)
        if creator is True and result is True:
            self.add_admin(inviter_id, invited_id, creator=creator)
        return result

    def rm_account(self, inviter_id, invited_id, committer):
        result = False
        if self.accounts.exists(invited_id):
            if self.check_admin(inviter_id) or inviter_id == invited_id:
                if len(self.accounts.ids) > 1:
                    result = self.accounts.remove(invited_id, committer=committer)
        return result

    def cv_add(self, cvobj, committer=None, unique=True, do_commit=True):
        result = self.curriculumvitaes.add(cvobj, committer,
                                          unique=unique, do_commit=do_commit)
        return result

    def cv_search(self, keyword):
        return self.curriculumvitaes.search(keyword, selected=self.config['storageCV'])

    def cv_search_yaml(self, keyword):
        return self.curriculumvitaes.search_yaml(keyword, selected=self.config['storageCV'])

    def cv_projects(self, id):
        return [p.name for p in self.projects.values() if id in p.cv_ids()]

    def getproject(self, projectname):
        return self.projects[projectname]

    def getnums(self):
        result = dict()
        result['total'] = 0
        for name in self.projects:
            project = self.projects[name]
            numbers = project.cv_numbers()
            result[name] = numbers
            result['total'] += numbers
        return result

    def backup(self, path):
        member_path = os.path.join(path, self.name)
        projects_path = os.path.join(member_path, 'projects')
        accounts_path = os.path.join(member_path, 'accounts')
        companies_path = os.path.join(member_path, 'companies')
        curriculumvitaes_path = os.path.join(member_path, 'curriculumvitaes')
        utils.builtin.assure_path_exists(member_path)
        utils.builtin.assure_path_exists(projects_path)
        utils.builtin.assure_path_exists(accounts_path)
        utils.builtin.assure_path_exists(companies_path)
        utils.builtin.assure_path_exists(curriculumvitaes_path)
        for name in self.projects:
            project = self.projects[name]
            project.backup(projects_path)
        self.accounts.backup(accounts_path)
        self.companies.backup(companies_path)
        self.curriculumvitaes.backup(curriculumvitaes_path)


class DefaultMember(Member):

    default_name = 'default'

    def __init__(self, acc_repos, cv_repos, mult_peo, path,
                 name='default', iotype='git'):
        super(DefaultMember, self).__init__(acc_repos, cv_repos,
                                            mult_peo, path, name, iotype=iotype)

    def load_projects(self):
        super(DefaultMember, self).load_projects()
        if self.default_name not in self.projects:
            super(DefaultMember, self)._add_project(self.default_name,
                                                    sources.industry_id.sources)
        self.projects[self.default_name].cv_secrecy = True
        self.projects[self.default_name]._modelname = self.default_model

    def use(self, id):
        return self

    def getproject(self, projectname=None):
        return self.projects[self.default_name]

    def add_admin(self, **kwargs):
        return False

    def add_account(self, **kwargs):
        return False

    def add_project(self, **kwargs):
        return False
