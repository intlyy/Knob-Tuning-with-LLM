import requests
import json
import pymysql
import os
import sys
import time
import re

mysql_ip = 
ip_password = ''
config = {
    'user': '',      
    'password': '',   
    'host': '',           
    'database': 'sysbench',   
    'port': 3306

}


def get_current_metric():

    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    sql = "select name,count from information_schema.INNODB_METRICS where status = 'enabled'"
    cursor.execute(sql)
    result = cursor.fetchall() 
    knobs = {}
    for i in result:
        #print(f"\"{i[0]}\" : {i[1]},")
        knobs[i[0]] = int(i[1])
    json_data = json.dumps(knobs, indent=4)
    #print(json_data)
    return knobs

def get_current_knob():

    conn = pymysql.connect(**config)
    cursor = conn.cursor()

    knobs = {}

    parameters = [
        'tmp_table_size', 'max_heap_table_size', 'query_prealloc_size', 'innodb_thread_concurrency',
        'sort_buffer_size', 'innodb_buffer_pool_size', 'innodb_max_dirty_pages_pct_lwm', 'innodb_purge_threads',
        'table_open_cache_instances', 'innodb_compression_failure_threshold_pct', 'innodb_purge_batch_size',
        'expire_logs_days', 'innodb_lru_scan_depth', 'innodb_max_dirty_pages_pct', 'innodb_write_io_threads',
        'innodb_stats_transient_sample_pages', 'div_precision_increment', 'innodb_spin_wait_delay',
        'innodb_compression_pad_pct_max', 'innodb_read_ahead_threshold'
    ]

    for param in parameters:
        cursor.execute(f"SHOW VARIABLES LIKE '{param}'")
        result = cursor.fetchone()
        if result:
            knobs[param] = int(result[1]) if result[1].isdigit() else round(float(result[1]))
            #print(f"\"{param}\": {result[1]}")

    json_data = json.dumps(knobs, indent=4)
    print(json_data)
    return knobs


def get_knobs_detail():
    f = open('', 'r')
    content = json.load(f)
    #content = set_expert_rule(content)

    result = {}
    count = 0
    for i in content.keys():
        result[i] = content[i]
        count += 1
    
    return result

def test_by_JOB(self,log_file):

    temp_config = {}
    knobs_detail = get_knobs_detail()
    for key in knobs_detail.keys():
        if key in knob.keys():
            if knobs_detail[key]['type'] == 'integer':
                temp_config[key] = knob.get(key) 
            elif knobs_detail[key]['type'] == 'enum':
                temp_config[key] = knobs_detail[key]['enum_values'][knob.get(key)]
    
    #set knobs and restart databases
    set_knobs_command = '\cp {} {};'.format('/etc/my.cnf.bak' , '/etc/my.cnf')
    for knobs in temp_config:
        set_knobs_command += 'echo "{}"={} >> {};'.format(knobs,temp_config[knobs],'/etc/my.cnf')
    
    head_command = 'sshpass -p {} ssh {} '.format(ip_password, mysql_ip)
    set_knobs_command = head_command + '"' + set_knobs_command + '"' 
    state = os.system(set_knobs_command)

    time.sleep(10)

    print("success set knobs")
    #exit()

    restart_knobs_command = head_command + '"service mysqld restart"' 
    state = os.system(restart_knobs_command)

    if state == 0:
        print('database has been restarted')
        conn = pymysql.connect(host=config.get('host'),
                    user=config.get('mysql_user'),
                    passwd=config.get('mysql_password'),
                    db=config.get('database'),
                    port=config.get('port'))
        cursor = conn.cursor()
        query_dir = ''
        query_files = [os.path.join(query_dir, f) for f in os.listdir(query_dir) if f.endswith('.sql')]
        total_time = 0
        i = 0 
        for i in range(1):
            i = i+1
            for query_file in query_files:
                print(f"Running {query_file}")
                elapsed_time = self.run_benchmark(query_file, cursor)
                print(f"Time taken: {elapsed_time:.2f} seconds")
                total_time += elapsed_time
        
        print(f"Total time for 5 runs: {total_time:.2f} seconds")

        cursor.close()
        conn.close()
        return total_time
    else:
        print('database restarting failed')
        return -1

    

    

def test_by_sysbench(knob):
    #load knobs
    temp_config = {}
    knobs_detail = get_knobs_detail()
    for key in knobs_detail.keys():
        if key in knob.keys():
            if knobs_detail[key]['type'] == 'integer':
                temp_config[key] = knob.get(key) 
            elif knobs_detail[key]['type'] == 'enum':
                temp_config[key] = knobs_detail[key]['enum_values'][knob.get(key)]
    
    #set knobs and restart databases
    set_knobs_command = '\cp {} {};'.format('/etc/my.cnf.bak' , '/etc/my.cnf')
    for knobs in temp_config:
        set_knobs_command += 'echo "{}"={} >> {};'.format(knobs,temp_config[knobs],'/etc/my.cnf')
    
    head_command = 'sshpass -p {} ssh {} '.format(ip_password, mysql_ip)
    set_knobs_command = head_command + '"' + set_knobs_command + '"' 
    state = os.system(set_knobs_command)

    time.sleep(10)

    print("success set knobs")
    #exit()

    restart_knobs_command = head_command + '"service mysqld restart"' 
    state = os.system(restart_knobs_command)

    if state == 0:
        print('database has been restarted')
        log_file = './LLM_result//log/' + '{}.log'.format(int(time.time()))
        command_run = 'sysbench --db-driver=mysql --threads=32 --mysql-host={} --mysql-port={} --mysql-user={} --mysql-password={} --mysql-db={} --tables=50 --table-size=1000000 --time=120 --report-interval=60 oltp_read_write run'.format(
                            config.get('host'),
                            config.get('port'),
                            config.get('user'),
                            config.get('password'),
                            config.get('database')
                            )
        
        os.system(command_run + ' > {} '.format(log_file))
        
        qps = sum([float(line.split()[8]) for line in open(log_file,'r').readlines() if 'qps' in line][-int(120/60):]) / (int(120/60))
        tps = float(qps/20.0)
        return tps
    else:
        print('database restarting failed')
        return 0

if __name__ == "__main__":

    knob = get_current_knob()
    throughput =  test_by_sysbench(knob)
    metric = get_current_metric()
    # prepare data
    data = {
        "knob": knob,
        "throughput": throughput,
        "metric": metric
        }  
    print(data)
    # server address and port
    url = ''


    # send message
    response = requests.post(url, json=data)

    # reply
    result = response.json()
    print(result.get('knob'))
    
    iteration = 0
    while iteration < 10:
        knob = result.get('knob')
        if(knob == 0): 
            print("ERROR!")
            break
        throughput =  test_by_sysbench(knob)
        if(throughput == 0):
            metric = []
        else:
            metric = get_current_metric()
        data = {
        "knob": knob,
        "throughput": throughput,
        "metric": metric
        }  
        if result.get('flag') == 1:
            with open('',"a") as f:
                json.dump(data, f, indent=4)
                f.close()
        else: print("No configuration in feedback, Retry")
            
        url = ''
        response = requests.post(url, json=data)
        
        result = response.json()
        iteration = iteration+1
