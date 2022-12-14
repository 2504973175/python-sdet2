import json
from flask import request, current_app as app
from constant import SQLTYPE, DBKEYTYPE
from lib.dbpool import DBPool


def idata():
    return query(request.json)

def onconnect():
    data=request.json
    conn_info = warp_db_conn_info(data)
    print(conn_info)
    db_conn = DBPool.get_conn(**conn_info)
    ret = {
        "success": False,
        "msg": None,
        'code':0
    }
    if not db_conn:
        ret['msg'] = '连接目标DB失败，请确认连接信息是否正确'
        ret['code']=-1
    else:
        ret['msg'] = '连接成功'
        ret['success']=True
        ret['code']=0
    return ret


def warp_db_conn_info(data):
    d = {}
    keys = ['db_host', 'db_port', 'db_name', 'db_user', 'db_passwd', 'db_charset']
    for key in keys:
        if key in data and data[key]:
            d[key] = data[key].strip() if isinstance(data[key], (str, bytes)) else data[key]

    return d


def query(data):
    """
    根据DB和SQL信息执行远程查询并返回结果
    :param data:     {
        "db_host": "x.x.x.x",
        "db_port": 3306,
        "db_name": "test",
        "db_user": "root",
        "db_passwd": "root",
        "db_charset": "utf8",
        "sql": "select * from tbl_key_info where id=:id limit 1",
        "param": {
            "id": 100110
        },
        "key": "all"
    }
    :return: {
        "success": True,
        "data": [{"id": 100110, "xxx", "xxx"}],
        "type": "SELECT",
        "msg": ""
    }
    """
    app.logger.info(f'query data {json.dumps(data)}')
    ret = {
        "success": False,
        "data": [],
        "type": None,
        "msg": None,
        "code":0
    }

    if not data:
        return ret

    conn_info = warp_db_conn_info(data)
    # print(conn_info)
    db_conn = DBPool.get_conn(**conn_info)
    if not db_conn:
        ret['msg'] = '连接目标DB失败，请确认连接信息是否正确'
        return ret

    sql = data.get('sql')
    if not sql:
        ret['msg'] = '查询语句不能为空'
        return ret

    # app.logger.info(f'查询语句: {sql}, 查询参数: {data.get("param")}')
    app.logger.info(f'查询语句: {sql}, 查询参数: {data.get("param")}')
    # rows = db_conn.query(sql, **data.get('param'))
    rows = db_conn.query(sql)
    results = []

    upper_sql = sql.upper().strip()
    if upper_sql.startswith(SQLTYPE.INSERT):
        sql_type = SQLTYPE.INSERT
    elif upper_sql.startswith(SQLTYPE.UPDATE):
        sql_type = SQLTYPE.UPDATE
    elif upper_sql.startswith(SQLTYPE.DELETE):
        sql_type = SQLTYPE.DELETE
    elif upper_sql.startswith(SQLTYPE.SELECT):
        sql_type = SQLTYPE.SELECT
        key = data.get('key', DBKEYTYPE.FIRST)
        if key == 'all':
            results = rows.as_dict()
        else:  # 为了减少网络传输，默认只查询一行
            first = rows.first()
            results = [first.as_dict()] if first else []
    else:
        sql_type = SQLTYPE.UNKNOWN

    ret.update(
        {
            "success": True,
            "data": results,
            "type": sql_type,
            "msg": '',
            'code':0

        }
    )

    app.logger.info(f'查询结果: {results}')
    return ret
