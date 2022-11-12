from flask import jsonify
from flask import request
from model.todo import *
import logging
from . import warp_date_field


def todo():

    data = request.json
    print('request.method', request.method)  # 获取请求方法
    print('request.url', request.url)  # 获取完整的URL
    # 请求头
    # print('request.headers', request.headers)  # 获取所有请求头里面的字段
    # print('request.cookies', request.cookies)

    print('request.json', request.json)




    if data.get('id'):  # 更新任务
        ret = update_todo(data)
    else:   # 新增任务
        ret = create_todo(data)

    code = 0 if ret else -1

    return jsonify({
        "code": code,
        "msg": '',
        "data": ret
    })


def get_todo_list():
    tab = request.args.get('tab')
    if tab == 'current':
        ret = get_current_todo()
    elif tab == 'unfinish':
        ret = get_unfinish_todo()
    elif tab == 'finished':
        ret = get_finished_todo()
    else:
        ret = []

    ret = warp_date_field(ret)#?????????????
    print(ret)
    return jsonify({
        "code": 0,
        "msg": '',
        "data": ret
    })
if __name__ == '__main__':
    todo()