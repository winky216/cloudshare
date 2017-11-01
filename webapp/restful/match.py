import flask
import flask.ext.login
from flask.ext.restful import reqparse
from flask.ext.restful import Resource

import core.mining.correlation


class MatchbaseAPI(Resource):

    decorators = [flask.ext.login.login_required]

    def __init__(self):
        self.miner = flask.current_app.config['SVC_MIN']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('doc', type = unicode, location = 'json')
        self.reqparse.add_argument('page', type = int, location = 'json')
        self.reqparse.add_argument('numbers', type = int, location = 'json')

    def post(self):
        args = self.reqparse.parse_args()
        self.doc = args['doc']
        self.page = args['page']
        self.numbers = args['numbers']


class JDmathAPI(MatchbaseAPI):

    def __init__(self):
        super(JDmathAPI, self).__init__()
        self.jd_repo = flask.current_app.config['SVC_JD_REPO']
        self.co_repo = flask.current_app.config['SVC_CO_REPO']

    def post(self):
        super(JDmathAPI, self).post()
        result = core.mining.correlation.jobdescription_correlation(self.miner, [self.jd_repo],
                    doc=self.doc, page=self.page, numbers=self.numbers)
        for each in result:
            each[2]['company'] = self.co_repo.getyaml(each[2]['company'])['name']
        return { 'code': 200, 'data': result }


class COmathAPI(MatchbaseAPI):

    def __init__(self):
        super(COmathAPI, self).__init__()
        self.cv_repo = flask.current_app.config['SVC_CV_REPO']

    def post(self):
        super(COmathAPI, self).post()
        result = core.mining.correlation.company_correlation(self.miner, [self.cv_repo],
                    doc=self.doc, page=self.page, numbers=self.numbers)
        return { 'code': 200, 'data': result }


class POSmathAPI(MatchbaseAPI):

    def __init__(self):
        super(POSmathAPI, self).__init__()
        self.cv_repo = flask.current_app.config['SVC_CV_REPO']

    def post(self):
        super(POSmathAPI, self).post()
        result = core.mining.correlation.position_correlation(self.miner, [self.cv_repo],
                    doc=self.doc, page=self.page, numbers=self.numbers)
        return { 'code': 200, 'data': result }


class PRJmathAPI(MatchbaseAPI):

    def __init__(self):
        super(PRJmathAPI, self).__init__()
        self.cv_repo = flask.current_app.config['SVC_CV_REPO']

    def post(self):
        super(PRJmathAPI, self).post()
        result = core.mining.correlation.project_correlation(self.miner, [self.cv_repo],
                    doc=self.doc, page=self.page, numbers=self.numbers)
        return { 'code': 200, 'data': result }