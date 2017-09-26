require([
    'jquery',
    'base/js/utils',
    'base/js/namespace',
    'services/sessions/session'
], function(
    $,
    utils,
    Jupyter,
    session
    ) {
    "use strict";

    var save_prototype_get_model = session.Session.prototype._get_model;
    session.Session.prototype._get_model = function () {
        var model = save_prototype_get_model.call(this);
        model.path= utils.get_body_data("sessionPath");
        return model;
    };

    Jupyter.shareSessionListNotebooks = function(dir,element) {
        var path = utils.get_body_data('sessionPath');
        element.append('<h2>Helper Notebooks in '+dir+'</h2>')
        Jupyter.notebook.contents.list_contents(utils.url_path_split(path)[0]+'/'+dir).then(
            function(list,msg) {
                for (var i in list.content) {
                    element.append(
                        '<a target="'
                        +list.content[i].path+'|'+path
                        +'" href="'+dir+'/'+list.content[i].name
                        +'?sharesession='+path+'">'
                        +list.content[i].name+'</a>');
                    element.append('<br>')
                }
            }, 
            function(error) {
                alert(error);
            }
        );
    };
})
