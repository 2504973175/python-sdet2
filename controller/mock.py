import os
import requests
from flask import request, current_app as app, jsonify
from lib.storage import Storage
from config import Config
from constant import NO_PATTERN_RESPONSE

conf = Config.get(os.environ.get('FLASK_ENV'), Config['default'])
print("conf.storage----{}".format(conf.storage))
storage = Storage.get(conf.storage)(conf)
# storage="MysqlStorage"
DEFAULT_HEADERS = {}


def imock_data():
    """
    imock_data用来处理Mock数据的设置、查看和删除请求
    :return:
    """
    if request.method == 'DELETE':
        data = request.json
        storage.remove(storage.make_key(data))

        return jsonify({'code': 0, 'data': storage.to_dict()})
    elif request.method == 'POST':
        data = request.json
        print("data>>>>>>>>>>>{}".format(data))
        key = storage.make_key(data)
        print("key>>>>>>>>>{}".format(key))
        storage.set(key, data)

        # return jsonify({'code': 0, 'data': storage.to_dict()})
        return jsonify({'code': 0, 'data': data})
    else:
        return jsonify({'code': 0, 'data': storage.to_dict()})


def imock():
    url = '/imock'
    print("url--------{}".format(url))
    print("request----->{}".format(request))
    print("conf---------->{}".format(conf))
    print("storage------->{}".format(storage))

    return make_response(url, request, conf, storage)


def imock_match(path):
    url = '/' + path

    return make_response(url, request, conf, storage)


def match_mock(url, request, storage):#查询数据库是否有对于mock
    # key_default = f"{request.host}:{url}:{request.method}"
    # print("key_default>>>>>>{}".format(key_default))#localhost:9528:/imock:POST
    # key_without_host = f"*:{url}:{request.method}"
    # print(key_without_host)
    # key_without_method = f"{request.host}:{url}:*"
    # print(key_without_method)
    # key_without_host_method = f"*:{url}:*"
    # print(key_without_host_method)
    data=request.json
    key = storage.make_key(data)
    return storage.get(key)
    # return jsonify({'code': 0, 'data': storage.get(key)})

    # return storage.get(key_default) or storage.get(key_without_host) or \
    # #         storage.get(key_without_method) or storage.get(key_without_host_method)


def get_proxy_response(req):
    app.logger.info("starting proxy")
    method = req.method
    print(method)
    url = req.url
    headers = dict(req.headers)
    req_instance = getattr(requests, method.lower())
    # req_instance = getattr(req, method.lower())
    # print(req_instance)
    # print(requests.method.lower())

    if method in ['GET', 'HEAD', 'OPTIONS']:
        rep = req_instance(url, headers=headers)
    elif method in ['PUT', 'POST', 'DELETE']:
        data = req.data or req.form
        print("data:{}".format(data))
        # files = req.files
        # if files:
        #     header_str = ['Content-Type', 'content-type']
        #     for h in header_str:
        #         if h in headers:
        #             headers.pop(h)
        # rep = req_instance(url, data=data, files=files, headers=headers)
        # rep = req_instance(url, data=data, headers=headers)
        rep=requests.post(url, data=data, headers=headers)
        print("11111111111111111111111111111111")
        print("rep:{}".format(rep))
    else:
        return '', 200, DEFAULT_HEADERS

    header_str = ['Connection', 'connection', 'Transfer-Encoding', 'transfer-encoding', 'Content-Encoding', 'content-encoding']
    for h in header_str:
        if h in rep.headers:
            rep.headers.pop(h)

    rep_headers = dict(rep.headers)
    print(rep.content)
    print(rep.status_code)
    print({**rep_headers, **DEFAULT_HEADERS})
    return rep.content, rep.status_code, {**rep_headers, **DEFAULT_HEADERS}


def make_response(url, request, conf, storage):
    print("url{},request{},conf{},storage{}".format(url,request,conf,storage))
    default_rep = '', 200, DEFAULT_HEADERS
    print("default_rep:{}".format(default_rep))
    #执行mock匹配
    mock = match_mock(url, request, storage) #None
    #mock:{'code': 200, 'headers': {'Content-Type': 'plain/html'}, 'data': 'Hello Python', 'no_pattern_response': 'empty', 'type': 'text'}
    print("mock:{}".format(mock))
    no_pattern_response = None

    if mock:      # mock set
        app.logger.info('匹配到mock')
        data = mock.get('data', '') #获取到mock数据的data值
        if data:
            headers = mock.get('headers', {})
            data = merge_data(mock, request)
            # return data, mock.get('code', 200), {**headers, **DEFAULT_HEADERS}
            return jsonify({'code': 0, 'data': data})

        no_pattern_response = mock.get('no_pattern_response')

    app.logger.info('no mock set')
    no_pattern_response = no_pattern_response or conf.no_pattern_response
    print("no_pattern_response:{}".format(no_pattern_response))
    print("conf.no_pattern_response{}".format(conf.no_pattern_response))
    if no_pattern_response == NO_PATTERN_RESPONSE.PROXY:
        app.logger.info('match proxy mode')
        if request.host in conf.proxy_exclude:
            app.logger.info('proxy exclude: %s' % conf.proxy_exclude)
            return default_rep
        return get_proxy_response(request)

    return default_rep


def merge_data(mock, req):
    # 动态参数化类型，返回格式化后的结果作为mock内容
    if mock.get('type') == 'dynamic':
        if req.method in ['POST', 'PUT', 'DELETE']:
            if 'application/json' in req.headers.get('Content-Type', ''):
                kw = req.json()
            else:
                kw = req.form
        else:
            kw = req.args
        data = mock.get('data').format(**kw)
    # Python表达式类型，返回表达式执行的结果作为mock内容
    elif mock.get('type') == 'express':
        data = eval(mock.get('data'))
    # 默认为纯文本
    else:
        data = mock.get('data')

    return data