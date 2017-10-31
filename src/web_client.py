# coding: utf-8
import web
from web import form

import config
import client

render = web.template.render('web_client/')
urls = (
  '/', 'index'
)
app = web.application(urls, globals())

clientconf = form.Form(
    form.Textbox(
        "Port", 
        form.notnull,
        form.Validator(
            "Must be between 1000 and 65535",
            lambda x: 1000 <= int(x) <= 65535
        ),
        value = config.CLIENT_PORT),
    form.Button('Start'),
    # form.Button('Kill')
)

class index: 
    def GET(self): 
        form = clientconf()
        return render.client(form)

    def POST(self): 
        form = clientconf() 
        if not form.validates(): 
            return render.client(form)
        else:
            client.reactor.listenTCP(int(form["Port"].value), client.MelkwegLocalProxyFactory())
            client.reactor.run()
            return "Success."

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
