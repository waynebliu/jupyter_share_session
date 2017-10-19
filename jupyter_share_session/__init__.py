import os
from tornado import web
HTTPError = web.HTTPError
from tornado import httpclient

from notebook.base.handlers import (
    IPythonHandler, FilesRedirectHandler, path_regex,
)
from notebook.utils import url_escape
import notebook.notebook.handlers

import os
MYPATH = os.path.dirname(__file__)
print('my extra template dir',MYPATH)

class ShareSessionHandler(IPythonHandler):
    @web.authenticated
    def get(self, path):
        """get renders the notebook template if a name is given, or 
        redirects to the '/files/' handler if the name is not given."""

        # split two-part urls: <sessionpath>/index.ipynb=<notebookpath>
        cm = self.contents_manager
        session_path, notebook_path = get_session_notebook_paths(path,cm)
        if session_path == notebook_path and not session_path.endswith('/index.ipynb'):
            # fall back to old behavior
            return self.old_get(path)

        notebook_path = notebook_path.strip('/')
        session_path = session_path.strip('/')
        download_path = notebook_path

        # will raise 404 on not found
        try:
            model = cm.get(notebook_path, content=False)
        except web.HTTPError as e:
            if e.status_code == 404:
                # 404 file not found by cm - let's try to download 
                download_path = try_download_url(self, session_path, notebook_path)
                if download_path != notebook_path:
                    # OK, downloaded something - let's try to open it as notebook
                    model = cm.get(download_path, content=False)
                else:
                    return FilesRedirectHandler.redirect_to_files(self, path)
            else:
                raise
        if model['type'] != 'notebook':
            # not a notebook, redirect to files
            return FilesRedirectHandler.redirect_to_files(self, path)

        # brute force hack to add this dir to template path
        if MYPATH not in self.settings['jinja2_env'].loader.searchpath:
            self.settings['jinja2_env'].loader.searchpath.append(MYPATH)
        print(self.settings['jinja2_env'].loader.searchpath)

        address_path = (session_path+'='+notebook_path).strip('/')
        print(session_path, notebook_path, download_path, address_path)

        name = notebook_path.rsplit('/', 1)[-1]
        self.write(self.render_template('sharesession.html',
            notebook_path=download_path,
            session_path=session_path,
            address_path=address_path,
            notebook_name=name,
            kill_kernel=False,
            mathjax_url=self.mathjax_url,
            mathjax_config=self.mathjax_config
            )
        )

def get_session_notebook_paths(path,cm):
    splitpath = path.split('.ipynb=')
    if len(splitpath) == 2:
        return splitpath[0]+'.ipynb', splitpath[1]
    # try to use ./index.ipynb if it exists in the directory
    try:
        session_path = path.rsplit('/', 1)[0]+'/index.ipynb'
        cm.get(session_path, content=False)
        return session_path, path
    except web.HTTPError as e:
        # no index.ipynb, or some other problem - use path as session
        return path,path

def try_download_url(self, session_path, notebook_path):
    '''
    '''
    # if it's a url that we can try to download file and save to 
    # a download location
    from urllib.parse import urlparse, quote, urlencode
    from urllib.request import urlopen
    try:
        download_base = session_path.rsplit('/', 1)[0]+'/Downloads/'
        result = urlparse(notebook_path)
        if not result.scheme:
            print('not a url',notebook_path)
            return notebook_path
        respath,resname = os.path.split(quote(result.path))
        download_path = download_base + quote(result.netloc) + respath
        os.makedirs(download_path, exist_ok=True)
        resfile = os.path.join(download_path,resname)
        if os.path.exists(resfile):
            print('file exists',resfile)
            return resfile
        print('fetching',notebook_path,'to',resfile)
        http_client = httpclient.HTTPClient()
        response = http_client.fetch( 
            "%s://%s%s" % (result.scheme,
                           result.netloc,
                           quote(result.path)),
            method=self.request.method,
            #body=self.request.body,
            headers=self.request.headers,
            )
        print('saving file',resfile)
        with open(resfile,'wb') as f:
            f.write( response.body )
        http_client.close()
        return resfile
    except Exception as e:
        print(e)
    print('got error',notebook_path)
    return notebook_path


from notebook.utils import url_path_join
def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """

    ### WHOA - MONKEY PATCH THE NOTEBOOK HANDLER!
    ShareSessionHandler.old_get = notebook.notebook.handlers.NotebookHandler.get
    notebook.notebook.handlers.NotebookHandler.get = ShareSessionHandler.get

    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], 
                                  r'notebooks(?P<path>.*)')
    web_app.add_handlers(host_pattern, [(route_pattern, ShareSessionHandler)])

