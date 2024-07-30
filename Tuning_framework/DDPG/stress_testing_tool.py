import os
import time
import time
import json
import config
import sys
import pymysql

class stress_testing_tool:
    def __init__(self,logger,knobs_detail,id):
        self.port = config.port
        self.host = config.host
        self.mysql_user = config.mysql_user
        self.mysql_password = config.mysql_password
        self.database = config.database
        self.tables = config.tables
        self.table_size = config.table_size
        self.runing_time = config.runing_time
        self.mysql_ip = config.mysql_ip
        self.ip_password = config.ip_password
        self.threads = config.threads
        self.logger = logger
        self.head_command = 'sshpass -p {} ssh {} '.format(self.ip_password,self.mysql_ip)
        self.benchmark = config.benchmark
        self.knobs_detail = knobs_detail
        self.id = id
        self.warm_up_time = config.warm_up_time
        self.mysql_cnf = config.mysql_cnf
        self.mysql_cnf_nak = config.mysql_cnf_bak
        self.rounds = 0

        #self.begining_warm_up()

    def begining_warm_up(self):
        command_run = 'sysbench --db-driver=mysql --threads={} --mysql-host={} --mysql-port={} --mysql-user={} --mysql-password={} --mysql-db={} --tables={} --table-size={} --time={} --report-interval=60 oltp_read_write run'.format(
                            self.threads,
                            self.host,
                            self.port,
                            self.mysql_user,
                            self.mysql_password,
                            self.database,
                            self.tables,
                            self.table_size,
                            1800
                            )
        
        os.system(command_run)

    def handle_HORD_config(self,config):
        temp_config = {}
        
        for index, key in enumerate(self.knobs_detail.keys()):
            temp_config[key] = int(config[index])
            
        y = self.test_config(temp_config)
        return y
    
    def handle_HEBO_config(self,config):
        temp_config = {}
        config = config.reset_index(drop=True)

        for key in self.knobs_detail.keys():
            temp_config[key] = int(config.loc[0,key])
        
        y = self.test_config(temp_config)
        return y
    
    def handle_SMAC_config(self,config,seed = 0):
        temp_config = {}
        for key in self.knobs_detail.keys():
            temp_config[key] = config[key]
        
        y = self.test_config(temp_config)
        return y

    def test_config(self,config):
        temp_config = {}
        for key in self.knobs_detail.keys():
                if self.knobs_detail[key]['type'] == 'integer':
                    if self.knobs_detail[key]['max'] > sys.maxsize:
                        temp_config[key] = int(config[key] * 10000)
                    else:
                        temp_config[key] = int(config[key])
                elif self.knobs_detail[key]['type'] == 'enum':
                    temp_config[key] = self.knobs_detail[key]['enum_values'][config[key]]

        
        self.rounds += 1
        self.logger.info(str(self.rounds) + ':' + json.dumps(temp_config))
        set_knobs_command = '\cp {} {};'.format(self.mysql_cnf_nak,self.mysql_cnf)
        for knob in temp_config:
            set_knobs_command += 'echo "{}"={} >> {};'.format(knob,temp_config[knob],self.mysql_cnf)
        
        set_knobs_command = self.head_command + '"' + set_knobs_command + '"' 
        state = os.system(set_knobs_command)

        time.sleep(10)

        restart_knobs_command = self.head_command + '"service mysqld restart"' 
        state = os.system(restart_knobs_command)

        if state == 0:
            self.logger.info('database has been restarted')
            log_file = './history_results/{}/log/'.format(self.id) + '{}.log'.format(int(time.time()))

            if self.benchmark == 'sysbench':
                y = self.test_by_sysbench(log_file)
            elif self.benchmark == 'tpcc':
                y = self.test_by_tpcc(log_file)

            conn = pymysql.connect(host=self.host,
                                    user=self.mysql_user,
                                    passwd=self.mysql_password,
                                    db=self.database,
                                    charset='utf8')
            cursor = conn.cursor()
            sql = "select count from information_schema.INNODB_METRICS where status = 'enabled'"
            cursor.execute(sql)
            result = cursor.fetchall() 
            metrics = []
            for i in result:
                metrics.append(i[0])
        else:
            self.logger.info('database restarting failed')
            y = 0
            metrics = []
        
        

        record = {}
        record['knobs'] = temp_config
        record['qps'] = y
        record['metrics'] = metrics
            
        f = open('./history_results/{}/records'.format(self.id),'a')
        f.writelines(json.dumps(record)+'\n')      
        f.close()
        time.sleep(5)

        return record

    def test_by_sysbench(self,log_file):
        command_run = 'sysbench --db-driver=mysql --threads={} --mysql-host={} --mysql-port={} --mysql-user={} --mysql-password={} --mysql-db={} --tables={} --table-size={} --time={} --report-interval=60 oltp_read_write run'.format(
                            self.threads,
                            self.host,
                            self.port,
                            self.mysql_user,
                            self.mysql_password,
                            self.database,
                            self.tables,
                            self.table_size,
                            self.warm_up_time + self.runing_time
                            )
        
        os.system(command_run + ' > {} '.format(log_file))

        qps = -sum([float(line.split()[8]) for line in open(log_file,'r').readlines() if 'qps' in line][-int(self.runing_time/60):]) / (int(self.runing_time/60))
        return qps
            

    def test_by_tpcc(self,log_file):
        command_run = './tpcc.lua --db-driver=pgsql --threads={} --pgsql-host={} --pgsql-port={} --pgsql-user={} --pgsql-password={} --pgsql-db={} --tables={} --scale={} --time={} --report-interval=60 run'.format(
                            self.threads,
                            self.host,
                            self.port,
                            self.user,
                            self.password,
                            self.database,
                            self.tables,
                            self.table_size,
                            self.warm_up_time + self.runing_time
                            )
        
        os.system(self.head_command + '"' + 'cd sysbench-tpcc-master;' + command_run + '"' + ' > {} '.format(log_file))

        qps = -sum([float(line.split()[8]) for line in open(log_file,'r').readlines() if 'qps' in line][-int(self.runing_time/60):]) / (int(self.runing_time/60))
        return qps







