import os

import utils.builtin
import core.outputstorage
import sources.industry_id
import services.base.service
import services.simulationcv
import services.simulationco
import services.simulationjd
import services.simulationpeo
import extractor.information_explorer

class Project(services.base.service.Service):

    CV_PATH = 'CV'
    CO_PATH = 'CO'
    JD_PATH = 'JD'
    PEO_PATH = 'PEO'
    config_file = 'config.yaml'

    def __init__(self, path, corepos, cvrepos, jdrepos, svcpeos, name, iotype='git'):
        super(Project, self).__init__(path, name, iotype=iotype)
        self.path = path
        self._modelname = name
        self.corepos = corepos
        self.jdrepos = jdrepos
        self.cvrepos = cvrepos
        self.svcpeos = svcpeos
        cvpath = os.path.join(path, self.CV_PATH)
        copath = os.path.join(path, self.CO_PATH)
        jdpath = os.path.join(path, self.JD_PATH)
        peopath = os.path.join(path, self.PEO_PATH)

        self.company = services.simulationco.SimulationCO(copath, name, corepos)
        self.curriculumvitae = services.simulationcv.SimulationCV(cvpath, name, cvrepos)
        self.jobdescription = services.simulationjd.SimulationJD(jdpath, name, jdrepos)
        self.people = services.simulationpeo.SimulationPEO(peopath, name, svcpeos)
        self.config = dict()
        try:
            self.load()
        except IOError:
            pass

    def load(self):
        self.config = utils.builtin.load_yaml(self.path, self.config_file)
        self.config['name'] = self.name
        if 'id' not in self.config:
            self.config['id'] = utils.builtin.genuuid()

    def save(self):
        dumpconfig = utils.builtin.dump_yaml(self.config)
        self.interface.add(self.config_file, dumpconfig, message="Update config file.")

    def setup(self, classify=None, committer=None, config=None):
        self.setconfig(config)
        self.setclassify(classify, committer=committer)

    def setconfig(self, config=None):
        if config is None:
            config = {}
        modified = False
        for key in config:
            if key not in self.config or self.config[key] != config[key]:
                self.config[key] = config[key]
                modified = True
        if modified:
            self.save()

    def setclassify(self, classify=None, committer=None):
        if not os.path.exists(os.path.join(self.path, self.config_file)) or classify is not None:
            self.config['classify'] = [c for c in classify if c in sources.industry_id.industryID]
            self.save()

    @property
    def storageCO(self):
        result = None
        servicename = self.config['storageCO']
        for corepo in self.corepos:
            if isinstance(corepo, services.simulationco.SimulationCO):
                for each in corepo.storages:
                    if each.name == servicename:
                        result = each
                        break
            elif corepo.name == servicename:
                result = each
            if result is not None:
                break
        return result

    @property
    def storageCV(self):
        result = None
        servicename = self.config['storageCV']
        for cvrepo in self.cvrepos:
            if isinstance(cvrepo, services.simulationcv.SimulationCV):
                for each in cvrepo.storages:
                    if each.name == servicename:
                        result = each
                        break
            elif cvrepo.name == servicename:
                result = each
            if result is not None:
                break
        return result

    @property
    def storageJD(self):
        result = None
        servicename = self.config['storageJD']
        for jdrepo in self.jdrepos:
            if isinstance(jdrepo, services.simulationjd.SimulationJD):
                for each in jdrepo.storages:
                    if each.name == servicename:
                        result = each
                        break
            elif jdrepo.name == servicename:
                result = each
            if result is not None:
                break
        return result

    @property
    def storagePEO(self):
        result = None
        servicename = self.config['storagePEO']
        for each in self.svcpeos[0].peoples:
            if each.name == servicename:
                result = each
                break
        return result

    @property
    def limitPEO(self):
        result = None
        servicename = self.config['limitPEO']
        for each in self.svcpeos[0].peoples:
            if each.name == servicename:
                result = each
                break
        return result

    @property
    def modelname(self):
        return self._modelname

    @property
    def id(self):
        return self.config['id']

    @property
    def cv_secrecy(self):
        return self.curriculumvitae.secrecy_default

    @property
    def cv_private(self):
        return self.curriculumvitae.private_default

    @cv_secrecy.setter
    def cv_secrecy(self, value):
        self.curriculumvitae.secrecy_default = value

    @cv_private.setter
    def cv_private(self, value):
        self.curriculumvitae.private_default = value

    @property
    def classify(self):
        result = [c for c in sources.industry_id.industryID]
        if 'classify' in self.config:
            result = self.config['classify']
        return result

    def getclassify(self):
        return self.classify

    def getindustry(self):
        result = dict()
        for each in self.classify:
            result.update({each: sources.industry_id.sources[each]})
        return result

    def cv_add(self, cvobj, committer=None, unique=True, do_commit=True):
        result = {
            'repo_cv_result' : False,
            'repo_peo_result' : False,
            'project_cv_result' : False,
            'project_peo_result' : False
        }
        peopmeta = extractor.information_explorer.catch_peopinfo(cvobj.metadata)
        peopobj = core.basedata.DataObject(data='', metadata=peopmeta)
        result['repo_cv_result'] = self.storageCV.add(cvobj, committer, unique=unique,
                                                      do_commit=do_commit)
        result['project_cv_result'] = self.curriculumvitae.add(cvobj, committer, unique=unique,
                                                               do_commit=do_commit)
        if result['repo_cv_result']:
            peoresult = self.peo_add(peopobj, committer, unique=unique, do_commit=do_commit)
            result.update(peoresult)
        return result

    def cv_add_eng(self, id, cvobj, committer):
        yaml_data = self.storageCV.getyaml(id)
        result = self.storageCV.add_md(cvobj, committer)
        yaml_data['enversion'] = cvobj.ID.md
        self.storageCV.modify(id+'.yaml', utils.builtin.dump_yaml(yaml_data), committer=committer)
        return result

    def cv_yamls(self):
        return self.curriculumvitae.yamls()

    def cv_names(self):
        return self.curriculumvitae.names()

    def cv_datas(self):
        return self.curriculumvitae.datas()

    def cv_count(self, keywords=None, filterdict=None, ids=None, selected=None):
        if selected is None:
            selected = [self.storageCV.name]
        if ids is None:
            ids = self.curriculumvitae.names()
        return self.curriculumvitae.count(keywords=keywords, filterdict=filterdict,
                                           ids=ids, selected=selected)

    def cv_count_yaml(self, keywords=None, filterdict=None, ids=None, selected=None):
        if selected is None:
            selected = [self.storageCV.name]
        if ids is None:
            ids = self.curriculumvitae.yamls()
        return self.curriculumvitae.count_yaml(keywords=keywords, filterdict=filterdict,
                                               ids=ids, selected=selected)

    def cv_search(self, keywords=None, filterdict=None, ids=None,
                  source=False, start=0, size=10, selected=None):
        if selected is None:
            selected = [self.storageCV.name]
        if ids is None:
            ids = self.curriculumvitae.names()
        return self.curriculumvitae.search(keywords=keywords, filterdict=filterdict,
                                           ids=ids, source=source,
                                           start=start, size=None, selected=selected)

    def cv_search_yaml(self, keywords=None, filterdict=None, ids=None,
                       source=False, start=0, size=10, selected=None):
        if selected is None:
            selected = [self.storageCV.name]
        if ids is None:
            ids = self.curriculumvitae.names()
        return self.curriculumvitae.search_yaml(keywords=keywords, filterdict=filterdict,
                                                ids=ids, source=source,
                                                start=start, size=size, selected=selected)

    def cv_gethtml(self, id):
        return self.curriculumvitae.gethtml(id)

    def cv_getmd(self, id):
        return self.curriculumvitae.getmd(id)

    def cv_getmd_en(self, id):
        return self.curriculumvitae.getmd_en(id)

    def cv_getyaml(self, id):
        return self.curriculumvitae.getyaml(id)

    def cv_numbers(self):
        return self.curriculumvitae.NUMS

    def cv_history(self, author=None, entries=10, skip=0):
        return self.curriculumvitae.history(author, entries, skip)

    def cv_updateyaml(self, id, key, value, username):
        result = None
        if key in dict(self.curriculumvitae.YAML_TEMPLATE):
            try:
                result = self.curriculumvitae.updateinfo(id, key, value, username)
            except AssertionError:
                pass
        return result

    def cv_ids(self):
        return self.curriculumvitae.ids

    def cv_timerange(self, start_y, start_m, start_d, end_y, end_m, end_d):
        return self.curriculumvitae.timerange(start_y, start_m, start_d,
                                              end_y, end_m, end_d)

    def company_update_info(self, id, info, committer):
        result = False
        if self.company.exists(id):
            repo_result = self.storageCO.saveinfo(id, info, "Update %s information."%id,
                                                  committer)
            project_result = self.company.update_info(id, info, committer)
            result = repo_result or project_result
        return result

    def company_compare_excel(self, stream, committer):
        outputs = list()
        outputs.extend(self.storageCO.compare_excel(stream, committer))
        outputs.extend(self.company.compare_excel(stream, committer))
        return outputs

    def company_add_excel(self, items, committer):
        results = dict()
        repo_result = set()
        project_result = set()
        for item in items:
            yamlname = core.outputstorage.ConvertName(item[1]).yaml
            if item[0] == 'companyadd':
                baseobj = core.basedata.DataObject(*item[2][:2])
                repo_result.add(yamlname)
                result = self.storageCO.add(baseobj, committer=item[2][-1], do_commit=False)
            elif item[0] == 'projectadd':
                baseobj = core.basedata.DataObject(*item[2][:2])
                project_result.add(self.company.ids_file)
                project_result.add(os.path.join(self.company.YAML_DIR, yamlname))
                result = self.company.add(baseobj, committer=item[2][-1], do_commit=False)
            elif item[0] == 'listadd':
                project_result.add(os.path.join(self.company.YAML_DIR, yamlname))
                result = self.company.updateinfo(*item[2], do_commit=False)
            results[item[1]] = result
        self.storageCO.interface.do_commit(list(repo_result), committer=committer)
        self.company.interface.do_commit(list(project_result), committer=committer)
        return results

    def company_add(self, coobj, committer=None, unique=True, yamlfile=True, mdfile=False):
        result = {
            'repo_result' : False,
            'project_result' : False
        }
        result['repo_result'] = self.storageCO.add(coobj, committer, unique, yamlfile, mdfile)
        if result['repo_result']:
            result['project_result'] = self.company.add(coobj, committer, unique,
                                                        yamlfile, mdfile)
        return result

    def company_get(self, name):
        return self.company.getyaml(name)

    def company_customers(self):
        return self.company.customers

    def company_names(self):
        return self.company.ids

    def jd_get(self, id):
        return self.jobdescription.getyaml(id)

    def jd_add(self, jdobj, committer=None, unique=True, do_commit=True):
        result = {
            'repo_result' : False,
            'project_result' : False
        }
        if self.company.exists(company):
            result['repo_result'] = self.storageJD.add(jdobj, committer,
                                                       unique=unique, do_commit=do_commit)
            if result['repo_result']:
                result['project_result'] = self.jobdescription.add(jdobj, committer,
                                                                unique=unique,
                                                                do_commit=do_commit)
        return result

    def jd_modify(self, id, description, status, commentary, followup, committer):
        result = False
        if self.jobdescription.exists(id):
            result = self.storageJD.modify(id, description, status,
                                           commentary, followup, committer)
        return result

    def jd_search(self, keyword, selected=None):
        return self.jobdescription.search(keyword, selected=selected)

    def jd_datas(self):
        return self.jobdescription.datas()

    def peo_add(self, peopobj, committer=None, unique=True, do_commit=True):
        result = {
            'repo_peo_result' : False,
            'project_peo_result' :False,
        }
        storage = self.storagePEO
        if peopobj.ID == peopobj.metadata['cv'][0]:
            storage = self.limitPEO
        result['repo_peo_result'] = storage.add(peopobj, committer,
                                                unique=unique, do_commit=do_commit)
        result['project_peo_result'] = self.people.add(peopobj, committer,
                                                       unique=unique, do_commit=do_commit)
        return result

    def peo_getyaml(self, id):
        return self.people.getyaml(id)

    def peo_updateyaml(self, id, key, value, username):
        result = None
        try:
            result = self.people.updateinfo(id, key, value, username)
        except AssertionError:
            pass
        return result

    def peo_deleteyaml(self, id, key, value, username, date):
        return self.people.deleteinfo(id, key, value, username, date)

    def backup(self, path, bare=True):
        backup_path = os.path.join(path, self.name)
        project_path = os.path.join(backup_path, 'project')
        cv_path = os.path.join(backup_path, 'curriculumvitae')
        jd_path = os.path.join(backup_path, 'jobdescription')
        co_path = os.path.join(backup_path, 'company')
        peo_path = os.path.join(backup_path, 'people')
        utils.builtin.assure_path_exists(project_path)
        utils.builtin.assure_path_exists(cv_path)
        utils.builtin.assure_path_exists(jd_path)
        utils.builtin.assure_path_exists(co_path)
        utils.builtin.assure_path_exists(peo_path)
        self.interface.backup(project_path, bare=bare)
        self.curriculumvitae.backup(cv_path, bare=bare)
        self.jobdescription.backup(jd_path, bare=bare)
        self.company.backup(co_path, bare=bare)
        self.people.backup(peo_path, bare=bare)
