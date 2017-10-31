
# coding: utf-8

# In[12]:


import web
from web import form


# In[13]:


import config
import client


# In[8]:


render = web.template.render('web_client/')
urls = (
  '/', 'index'
)
app = web.application(urls, globals())


# In[ ]:


# myform = form.Form( 
#     form.Textbox("boe"), 
#     form.Textbox("bax", 
#         form.notnull,
#         form.regexp('\d+', 'Must be a digit'),
#         form.Validator('Must be more than 5', lambda x:int(x)>5)),
#     form.Textarea('moe'),
#     form.Checkbox('curly'), 
#     form.Dropdown('french', ['mustard', 'fries', 'wine'])) 


# In[9]:


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
    form.Button('Kill')
)


# In[11]:


class index: 
    def GET(self): 
        form = clientconf()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return render.client(form)

    def POST(self): 
        form = clientconf() 
        if not form.validates(): 
            return render.client(form)
        else:
            client.reactor.listenTCP(int(form["Port"].value), client.MelkwegLocalProxyFactory())
            client.reactor.run()
            return "Success."


# In[ ]:


if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()

