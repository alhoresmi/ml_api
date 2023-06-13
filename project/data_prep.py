import json
import numpy as np
import pandas as pd
import pickle
import re
from sklearn.ensemble import RandomForestClassifier as rfc


def parse_request(d):
    d = str(d)
    d = d.replace("'", '"')
    d = d.replace('"{', '{')
    d = d.replace('}"}', '}}')
    d = json.loads(d)
    d = pd.json_normalize(d)
    d.columns = [v.split('.')[1] for v in d.columns]

    return d


def feature_engineering(d):
    #### clean and prepare data
    # CLIENT IP
    d["CLIENT_IP"].fillna("NONE", inplace=True)

    def ip_str(v, ip_pattern):
        return 1 if re.match(ip_pattern, v) else 0

    ip_pattern = "^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$"
    d["_ipv4"] = d["CLIENT_IP"].apply(lambda v: ip_str(v, ip_pattern))
    ip_pattern = "^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){3}))|:)))(%.+)?\s*$"
    d["_ipv6"] = d["CLIENT_IP"].apply(lambda v: ip_str(v, ip_pattern))


    # CLIENT_USERAGENT
    d["CLIENT_USERAGENT"].fillna("NONE", inplace=True)
    d["_useragent_len"] = d["CLIENT_USERAGENT"].apply(len)

    # REQUEST_SIZE
    d["_req_size_none"] = 1*d["REQUEST_SIZE"].isna()
    d["_req_size_string"] = 1*d["REQUEST_SIZE"].apply(lambda v: len(str(v)) > 10)

    d["REQUEST_SIZE"].fillna("0", inplace=True)
    def reqsize2number(s):
        if isinstance(s, str) and len(s) > 10:
            s = "0"
        return int(s)

    d["REQUEST_SIZE"] = d["REQUEST_SIZE"].apply(reqsize2number)

    # RESPONSE_CODE
    d["_resp_code_none"] = 1*d["RESPONSE_CODE"].isna()
    d["RESPONSE_CODE"].fillna("0")
    def code2int(s):
        if s is np.NAN:
            s = "0"
        elif len(str(s)) > 3:
            s = "0"
        return int(s)

    def code2grp(v):
        return v//100*100

    d["RESPONSE_CODE"] = d["RESPONSE_CODE"].apply(code2int)
    d["_resp_code_grp"] = d["RESPONSE_CODE"].apply(code2grp)

    d["MATCHED_VARIABLE_SRC"].fillna("NONE", inplace=True)
    d["MATCHED_VARIABLE_NAME"].fillna("NONE", inplace=True)

    # MATCHED_VARIABLE_VALUE
    d["MATCHED_VARIABLE_VALUE"].fillna("NONE", inplace=True)
    def susp_commands(s, commands):
        s = s.lower()
        susp = 0
        for temp in commands:
            if temp in s:
                susp = 1
                break
        return susp

    sql_commands = ['select', 'union', 'and ', 'or ']
    d["_matched_variable_value_sql"] = 1*d["MATCHED_VARIABLE_VALUE"].apply(lambda v: susp_commands(v, sql_commands))

    rce_commands = ['ls -la', 'echo', 'exec', 'eval', 'print', 'factor', '<script', ':usb', 'response.write']
    d["_matched_variable_value_rce"] = 1*d["MATCHED_VARIABLE_VALUE"].apply(lambda v: susp_commands(v, rce_commands))

    path_commands = ['../', '%5c', '0xf2', '%u2216']
    d["_matched_variable_value_path"] = 1*d["MATCHED_VARIABLE_VALUE"].apply(lambda v: susp_commands(v, path_commands))

    return d


def get_result(d, model):
    col = [
        'REQUEST_SIZE',
        'RESPONSE_CODE',
        '_ipv4',
        '_ipv6',
        '_useragent_len',
        '_req_size_none',
        '_req_size_string',
        '_resp_code_none',
        '_resp_code_grp',
    ]
    d['p'] = model.predict(d[col])

    result = []
    r = {}
    for i in range(len(d)):
        r['EVENT_ID'] = d['EVENT_ID'][i]
        r['LABEL_PRED'] = str(d['p'][i])
        result.append(r)

    return result
