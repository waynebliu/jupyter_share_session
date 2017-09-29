import os
from tornado import web
HTTPError = web.HTTPError

from notebook.base.handlers import (
    IPythonHandler, FilesRedirectHandler, path_regex,
)
from notebook.utils import url_escape
import notebook.notebook.handlers

import os
mypath = os.path.dirname(__file__)
print('my extra template dir',mypath)

class ShareSessionHandler(IPythonHandler):
    @web.authenticated
    def get(self, path):
        """get renders the notebook template if a name is given, or 
        redirects to the '/files/' handler if the name is not given."""

        # brute force hack to add . to template path
        if mypath not in self.settings['jinja2_env'].loader.searchpath:
            self.settings['jinja2_env'].loader.searchpath.append(mypath)
        print(self.settings['jinja2_env'].loader.searchpath)

        # split two-part urls: <sessionpath>/index.ipynb=<notebookpath>
        cm = self.contents_manager
        splitpath = path.split('/index.ipynb=')
        if len(splitpath) == 2:
            session_path = splitpath[0]+'/index.ipynb'
        else:
            # try to use ./index.ipynb if it exists in the directory
            try:
                session_path = path.rsplit('/', 1)[0]+'/index.ipynb'
                model = cm.get(session_path, content=False)
            except web.HTTPError as e:
                if e.status_code == 404:
                    # no index.ipynb - use path as session
                    session_path = path
                else:
                    raise
        path = path.strip('/')
        session_path.strip('/')
        
        # will raise 404 on not found
        try:
            model = cm.get(path, content=False)
        except web.HTTPError as e:
            if e.status_code == 404:
                # 404 - check if it's a url that we can try to download
                # path and save to download
                #import urllib
                #download_path = session_path.rsplit('/', 1)[0]+'/Downloads/'
                #url = urllib.open(path)
                raise
            else:
                raise
        if model['type'] != 'notebook':
            # not a notebook, redirect to files
            return FilesRedirectHandler.redirect_to_files(self, path)
        name = path.rsplit('/', 1)[-1]
        self.write(self.render_template('sharesession.html',
            notebook_path=path,
            session_path=session_path,
            notebook_name=name,
            kill_kernel=False,
            mathjax_url=self.mathjax_url,
            mathjax_config=self.mathjax_config
            )
        )



from notebook.utils import url_path_join
def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """

    ### WHOA - MONKEY PATCH THE NOTEBOOK HANDLER!
    notebook.notebook.handlers.NotebookHandler.get = ShareSessionHandler.get

    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], '/sharesession%s' % path_regex)
    web_app.add_handlers(host_pattern, [(route_pattern, ShareSessionHandler)])

