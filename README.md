
# Use cases

1. You want to split up your notebook into multiple files. 
    - Simply create a file "index.ipynb" in the directory where the files will be.
    - When you open a file in this directory, it will share the same session (same running kernel) as all the others
    - Note if the url path of the file you open is originally

            http://<hostname>:<port>/notebooks/<projectpath>/<file>.ipynb
      then brower address bar will be changed to 

            http://<hostname>:<port>/notebooks/<projectpath>/index.ipynb=<projectpath>/<file>.ipynb
      and the browser window will title change to "`<projectdir>:<file>`"

2. You have some common files that you want to share among multiple projects (i.e. in multiple notebook directories).
    - You can open the common file using url path:

            <projectpath>/index.ipynb=<commonutilpath>/<utilfile>.ipynb
    - The utilfile.ipynb page will run in the same kernel.
    - The simple way to make this url path is to use a relative path from within a Markdown cell in the index.ipynb. Use this Markdown link:
    
            [utilfile](../commonutildir/utilfile)

3. You have a website full of documentation notebooks, and you want your readers to browse the documentation without first downloading all the documentation files.
    - First, create index.pynb file, with `http://` links to the documentation notebooks on your website.  The format of the links will be:
    
            <basedocpath>/index.ipynb=http://<yourwebsite>/<docpath>/<docfile>.ipynb
    - Then your users can choose to download the index.ipynb, and open it in their local jupyter.
    - Alternatively, you can put your index.ipynb file on a hosted jupyter environment (such as [Binder](http://mybinder.org/)), and have your users open the link to index.ipynb running on that environment.


# New behavior

In any of the 3 use cases:
- the window url for these notebooks will be 

            http://<host>:<port>/notebooks/<projectpath>/index.ipynb=<notebookurl>
- all lrunning notebooks with the same `<projectpath>/index.ipynb=` will run within the same kernel
- the window title for these notebooks will be "projectdir:notebookname"


# Installation


```python
!pip install jupyter_share_session
```

Add the following line to `~/.jupyter/jupyter_notebook_config.json`:

        {
          "NotebookApp": {
        ...
            "nbserver_extensions": {
        ...
              "jupyter_share_session": true
            }
          }
        }


# Example notebooks

TBD

# Issues

1. The implementation is necessarily fragile and dependent on implementation details of Jupyter notebook.
    - It would be better if this behavior was included in JupyterLab directly, or there would be cleaner hooks to implement this as an extension.
- Integration with mybinder.org
- Conda installation?
- Integration with jupyter_contrib_extensions?
- Integration with jupyter_cms?
