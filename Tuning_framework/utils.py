import json
import logging
import pandas as pd
import config
import subprocess
from keras.models import load_model
import numpy as np



def get_logger(log_file):
    path = log_file + '/tune_database.log'
    logger = logging.getLogger('log')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(path)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('[%(asctime)s:%(filename)s#L%(lineno)d:%(levelname)s]: %(message)s'))

    logger.addHandler(handler)
    return logger

def get_knobs_detail():
    f = open(config.knobs_file, 'r')
    content = json.load(f)
    print("content!!!")
    print(content)
    #content = set_expert_rule(content)

    result = {}
    count = 0
    for i in content.keys():
        result[i] = content[i]
        count += 1
    print("count!!!")
    print(count)
    print( config.knobs_number)
    if count == config.knobs_number:
        print(result)
        return result
    else:
        print("ERROR!")

def set_expert_rule(content):
    command = 'sshpass -p {} ssh {} "free -h"'.format(config.omm_password,config.opengauss_ip)
    memory_Byte = int(subprocess.getoutput(command).split()[7][:-1]) * 1024 * 1024 * 1024

    if 'max_heap_table_size' in content:
        content['max_heap_table_size']['max'] = int(memory_Byte)

    if 'tmp_table_size' in content:
        content['tmp_table_size']['max'] = int(content['max_heap_table_size']['max'])

    if 'maintenance_work_mem' in content:
        content['maintenance_work_mem']['max'] = int(memory_kb)

    if 'work_mem' in content:
        content['work_mem']['max'] = int(memory_kb)

    if 'effective_cache_size' in content:
        content['effective_cache_size']['max'] = int(memory_kb / 8)

    return content

def safe_check(metric_cur,knobs_cur,knobs_sug):
    metrics = []
    data_x = []

    metrics.append(np.array(metric_cur))
    data_x.append(np.array(list(knobs_cur.values())))

    with open('./predictor/records', 'r') as f:
        lines = f.readlines()
        for l in lines:
            js = json.loads(l)
            qps = -float(js['qps'])
            if qps == 0:
                continue
            m = js['metrics']
            knobs = []
            for k in js['knobs']:
                knobs.append(js['knobs'][k])
            metrics.append(np.array(m))
            data_x.append(np.array(knobs))

    data_x = np.array(data_x)
    metrics = np.array(metrics)

    mmax = metrics.max(axis=0)
    mmin = metrics.min(axis=0)

    kmax = data_x.max(axis=0)
    kmin = data_x.min(axis=0)

    # 找出没有变化的metric
    flag = mmax != mmin

    # 去掉没有变化的metric
    metrics = metrics[:, flag]

    mmax = mmax[flag]
    mmin = mmin[flag]

    metric = np.divide(np.subtract(metrics[0], mmin), np.subtract(mmax, mmin))

    x0 = np.divide(np.subtract(data_x[0], kmin), np.subtract(kmax, kmin))
    x1 = np.divide(np.subtract(np.array(list(knobs_sug.values())), kmin), np.subtract(kmax, kmin))

    # 归一化
    # 加载模型
    model = load_model('./predictor/model_82.h5')
    # 构建输入：数据库状态+当前参数+新参数
    tmp = []
    tmp.append(np.hstack((metric, x0, x1)))
    x_pred = np.array(tmp)
    # 预测结果：1 安全，0 不安全
    y_pred = model.predict(x_pred)

    return y_pred[0][0]



