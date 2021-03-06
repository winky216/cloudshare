import webapp.server
import webapp.utils.log


app = webapp.server.app
if __name__ == '__main__':
    webapp.utils.log.init_smslog(app)
    if app.debug is False:
        webapp.utils.log.init_webapp_userlog(app)
    app.run(**app.config['APP_CONFIG'])
