import re
import logging
from lib.dbpool import DBPool


def warp_db_conn_info(data):
    d = {}
    keys = ['db_host', 'db_port', 'db_name', 'db_user', 'db_passwd', 'db_charset']
    for key in keys:
        if key in data and data[key]:
            d[key] = data[key].strip() if isinstance(data[key], (str, bytes)) else data[key]

    return d


def get_db():
    """数据库连接信息"""
    conn_info = {'db_host': 'localhost',
                 'db_name': 'iapi',
                 'db_user': 'root',
                 'db_passwd': '62015991yyl'}
    return DBPool.get_conn(**conn_info)


def query_with_pagination(conn, sql, param, page, size):
    """分页查询"""
    r = re.split('from', sql, flags=re.IGNORECASE)
    if len(r) == 1:
        logging.error(f'sql error: {sql}')
        return [], 0

    header_sql, main_sql = r
    count_sql = f"""select count(1) as total from {main_sql}"""

    logging.info(f'query count sql: {count_sql}, with param: {param}')
    queried_count = conn.query(count_sql, **param).first()
    total = queried_count.total if queried_count else 0

    skip = (int(page) - 1) * int(size)
    page_sql = f"""{header_sql} from {main_sql} limit {skip},{size}"""

    logging.info(f'query page sql: {page_sql}, with param: {param}')
    queried_records = conn.query(page_sql, **param).all()
    records = [r.as_dict() for r in queried_records]

    return records, total

if __name__ == '__main__':
    sql="""select * from task"""
    rows = get_db().query(sql).all(as_dict=True)
    print(rows)