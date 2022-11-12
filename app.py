import os
from flask import Flask
from controller.index import index
from controller.user import login, get_user_info, logout
from controller.todo import todo, get_todo_list
from controller.data import idata,onconnect
from controller.mock import imock,imock_data,imock_match
from controller import http
from controller import hproxy
from config import Config
from lib.storage import Storage
conf = Config.get(os.environ.get('FLASK_ENV'), Config['default'])
print("conf:{}".format(conf))
storage = Storage.get(conf.storage)(conf)
print("storage:{}".format(storage))
def create_app():
    app = Flask(__name__, static_url_path='/do_not_use_this_path__')
    app.config.from_object(conf)
    app.route('/api/_mock_settings_', methods=['GET', 'POST', 'DELETE'])(imock_data)
    app.route('/api/imock', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'OPTIONS'])(imock)
    app.route('/＜path:path＞', methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE',
                                       'OPTIONS'])(imock_match)
    app.route('/')(index)
    app.route('/api/user/login', methods=['POST'])(login)
    app.route('/api/user/info')(get_user_info)
    app.route('/api/user/logout', methods=['POST'])(logout)
    app.route('/api/todo', methods=['POST'])(todo)
    app.route('/api/todo/list')(get_todo_list)
    app.route('/api/idata', methods=['POST'])(idata)
    app.route('/api/test',methods=['POST'])(onconnect)
    # http api
    app.route('/api/http/', methods=['POST', 'GET'])(http.http_save)
    app.route('/api/http/file', methods=['POST', 'DELETE'])(http.http_file)
    app.route('/api/http/debug', methods=['POST'])(http.http_debug)
    # httplist
    app.route('/api/http/list', methods=['GET'])(http.http_list)
    app.route('/api/http/run/<int:aid>', methods=['GET'])(http.http_run)
    app.route('/api/http/api/log/<int:aid>', methods=['GET'])(http.http_api_log)
    # http log
    app.route('/api/http/log/list', methods=['GET'])(http.http_log_list)
    app.route('/api/http/log/<int:lid>', methods=['GET'])(http.http_log)

    return app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=9528, debug=True, threaded=True)
