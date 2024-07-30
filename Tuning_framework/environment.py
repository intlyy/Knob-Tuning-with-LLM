import datetime
import logging
import os
import sys
from abc import ABC
from collections import deque
import numpy as np
import paramiko
import psycopg2
import gym
from gym import spaces
from gym.utils import seeding

from configs import get_knob_config, get_ssh_config, get_database_config, get_workload
import time

from predictor import Predictor
from run_job import run_job

import executor


class Database:
    def __init__(self):
        self.internal_metric_num = int(get_database_config()['inner_metric_num'])
        self.external_metric_num = 2  # [throughput, latency]           # num_event / t
        self.knob_config = get_knob_config()
        self.database_config = get_database_config()
        self.max_connections_num = None
        self.knob_names = ["'" + knob['name'] + "'" for knob in self.knob_config]
        print("knob_names:", self.knob_names)
        print(len(self.knob_names))
        self.knob_num = len(self.knob_config)
        self.max_connections()

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=get_ssh_config()['host'],
                         port=int(get_ssh_config()['port']),
                         username=get_ssh_config()['user'],
                         password=get_ssh_config()['password']
                         )

    def get_conn(self):
        conn = psycopg2.connect(database=self.database_config["database"],
                                user=self.database_config["user"],
                                password=self.database_config["password"],
                                host=self.database_config["host"],
                                port=int(self.database_config["port"]))
        return conn

    # def fetch_internal_metrics(self):
    #     state_list = []
    #     # load average
    #     cpu_cores = self.exec_command_on_host("lscpu | grep 'CPU(s)' | head -1 | awk '{print $2}'")
    #     tmp = self.exec_command_on_host("cat /proc/loadavg")
    #     load_average = list(map(lambda v: float(v) / int(cpu_cores), tmp.strip().split(" ")[:3]))[0]
    #     state_list.append(load_average)
    #     # cache_hit_rate
    #     cache_hit_rate_sql = "select blks_hit / (blks_read + blks_hit + 0.001) " \
    #                          "from pg_stat_database " \
    #                          "where datname = '{}';".format(self.database_config["database"])
    #
    #     # database-wide statistics from pg_stat_database view
    #     DATABASE_STAT = """
    #     SELECT
    #       sum(numbackends) as numbackends,
    #       sum(xact_commit) as xact_commit,
    #       sum(xact_rollback) as xact_rollback,
    #       sum(blks_read) as blks_read,
    #       sum(blks_hit) as blks_hit,
    #       sum(tup_returned) as tup_returned,
    #       sum(tup_fetched) as tup_fetched,
    #       sum(tup_inserted) as tup_inserted
    #     FROM
    #       pg_stat_database;
    #     """
    #
    #     """
    #       sum(tup_updated) as tup_updated,
    #       sum(tup_deleted) as tup_deleted,
    #       sum(conflicts) as conflicts,
    #       sum(temp_files) as temp_files,
    #       sum(temp_bytes) as temp_bytes,
    #       sum(deadlocks) as deadlocks,
    #       sum(blk_read_time) as blk_read_time,
    #       sum(blk_write_time) as blk_write_time
    #     """
    #
    #     # database-wide statistics about query cancels occurring due to conflicts from pg_stat_database_conflicts view
    #     DATABASE_CONFLICTS_STAT = """
    #     SELECT
    #       sum(confl_tablespace) as confl_tablespace,
    #       sum(confl_lock) as confl_lock,
    #       sum(confl_snapshot) as confl_snapshot,
    #       sum(confl_bufferpin) as confl_bufferpin,
    #       sum(confl_deadlock) as confl_deadlock
    #     FROM
    #       pg_stat_database_conflicts;
    #     """
    #
    #
    #     """
    #       sum(seq_scan) as seq_scan,
    #       sum(seq_tup_read) as seq_tup_read,
    #     """
    #     # table statistics from pg_stat_user_tables view
    #     TABLE_STAT = """
    #     SELECT
    #       sum(idx_scan) as idx_scan,
    #       sum(idx_tup_fetch) as idx_tup_fetch
    #     FROM
    #       pg_stat_user_tables;
    #     """
    #
    #     """
    #         ,
    #       sum(n_tup_ins) as n_tup_ins,
    #       sum(n_tup_upd) as n_tup_upd,
    #       sum(n_tup_del) as n_tup_del,
    #       sum(n_tup_hot_upd) as n_tup_hot_upd,
    #       sum(n_live_tup) as n_live_tup,
    #       sum(n_dead_tup) as n_dead_tup,
    #       sum(vacuum_count) as vacuum_count,
    #       sum(autovacuum_count) as autovacuum_count,
    #       sum(analyze_count) as analyze_count,
    #       sum(autoanalyze_count) as autoanalyze_count
    #     """
    #
    #     try:
    #         conn = self.get_conn()
    #         cursor = conn.cursor()
    #         cursor.execute(cache_hit_rate_sql)
    #         result = cursor.fetchall()
    #         for s in result:
    #             state_list = np.append(state_list, s[0])
    #
    #         cursor.execute(DATABASE_STAT)
    #         result = cursor.fetchall()
    #         for i in result[0]:
    #             state_list = np.append(state_list, i)
    #
    #         # cursor.execute(DATABASE_CONFLICTS_STAT)
    #         # result = cursor.fetchall()
    #         # for i in result[0]:
    #         #     state_list = np.append(state_list, i)
    #
    #         cursor.execute(TABLE_STAT)
    #         result = cursor.fetchall()
    #         for i in result[0]:
    #             state_list = np.append(state_list, i)
    #
    #         cursor.close()
    #         conn.close()
    #     except Exception as error:
    #         print(error)
    #     # print("######inner_metrics######")
    #     # print(state_list)
    #     # print("######len = {}######".format(len(state_list)))
    #     return state_list

    def fetch_inner_metric(self):
        state_list = []
        conn = self.get_conn()
        cursor = conn.cursor()

        # ['cpu_useage','memory_useage','kB_rd/s','kB_wr/s','cache_hit_rate','concurrent_users','lock_wait_count','error_rate','logical_reads_per_second','physical_reads_per_second','active_session','transactions_per_second','rows_scanned_per_second','rows_updated_per_second','rows_deleted_per_second']
        # cpu和内存占用率s
        stdin, stdout, stderr = self.ssh.exec_command("top -b -n 1")
        lines = stdout.readlines()
        gaussdb_line = None
        for line in lines:
            if 'gaussdb' in line:
                gaussdb_line = line
                break
        if gaussdb_line:
            columes = gaussdb_line.split()
            cpu_usage = columes[8]
            state_list.append(cpu_usage)
            mem_usage = columes[9]
            state_list.append(mem_usage)
        else:
            print("gaussdb process not found in top output.")

        # 每秒读取和写入的kB数，kB_rd/s,kB_wr/s
        stdin, stdout, stderr = self.ssh.exec_command("pidstat -d")
        lines = stdout.readlines()[1:]
        gaussdb_line = None
        for line in lines:
            if 'gaussdb' in line:
                gaussdb_line = line
                break
        if gaussdb_line:
            columes = gaussdb_line.split()
            kB_rd = columes[3]
            state_list.append(kB_rd)
            kB_wr = columes[4]
            state_list.append(kB_wr)
        else:
            print("gaussdb process not found in pidstat")

        # cache_hit_rate
        cache_hit_rate_sql = "select blks_hit / (blks_read + blks_hit + 0.001) " \
                             "from pg_stat_database " \
                             "where datname = '{}';".format(get_database_config()['database'])

        # 并发用户数量
        concurrent_users = """
        SELECT
            count(DISTINCT usename)
        AS
            concurrent_users
        FROM
            pg_stat_activity
        WHERE
            state = 'active';
        """

        # 锁等待次数
        lock = """
        SELECT
            count(*) AS lock_wait_count
        FROM
            pg_stat_activity
        WHERE
            waiting = true;
        """

        # 错误率
        error_rate = """
        SELECT
            (sum(xact_rollback) + sum(conflicts) + sum(deadlocks)) / (sum(xact_commit) + sum(xact_rollback) + sum(conflicts) + sum(deadlocks)) AS error_rate
        FROM
            pg_stat_database;
        """

        # 逻辑读/秒和物理读/秒
        read = """
        SELECT
            logical_reads / (extract(epoch from now() - stats_reset)) AS logical_reads_per_second,
            physical_reads / (extract(epoch from now() - stats_reset)) AS physical_reads_per_second
        FROM (
            SELECT
                sum(tup_returned + tup_fetched) AS logical_reads,
                sum(blks_read) AS physical_reads,
                max(stats_reset) AS stats_reset
            FROM
                pg_stat_database
            ) subquery;
        """

        # 活跃会话数量
        active_session = """
        SELECT
            count(*) AS active_session
        FROM
            pg_stat_activity;
        """

        # 每秒提交的事务数
        transactions_per_second = """
        SELECT
            total_commits / (extract(epoch from now() - max_stats_reset)) AS transactions_per_second
        FROM (
            SELECT
            sum(xact_commit) AS total_commits,
            max(stats_reset) AS max_stats_reset
        FROM
            pg_stat_database
            ) subquery;
        """

        # 扫描行、更新行和删除行
        tup = """
        SELECT
            rows_scanned / (extract(epoch from now() - max_stats_reset)) AS rows_scanned_per_second,
            rows_updated / (extract(epoch from now() - max_stats_reset)) AS rows_updated_per_second,
             rows_deleted / (extract(epoch from now() - max_stats_reset)) AS rows_deleted_per_second
        FROM (
            SELECT
            sum(tup_returned) AS rows_scanned,
            sum(tup_updated) AS rows_updated,
            sum(tup_deleted) AS rows_deleted,
            max(stats_reset) AS max_stats_reset
            FROM
             pg_stat_database
            ) subquery;
        """

        try:
            cursor.execute(cache_hit_rate_sql)
            result = cursor.fetchall()
            for s in result:
                state_list.append(float(s[0]))

            # 并发用户数量
            cursor.execute(concurrent_users)
            result = cursor.fetchall()
            state_list.append(float(result[0][0]))

            # 锁等待次数
            cursor.execute(lock)
            result = cursor.fetchall()
            state_list.append(float(result[0][0]))

            # 错误率
            cursor.execute(error_rate)
            result = cursor.fetchall()
            state_list.append(float(result[0][0]))

            # 逻辑读和物理读
            cursor.execute(read)
            result = cursor.fetchall()
            # print(result)
            for i in result[0]:
                state_list.append(float(i))

            # 活跃会话数
            cursor.execute(active_session)
            result = cursor.fetchall()
            # print(result)
            state_list.append(float(result[0][0]))

            # 每秒提交的事务
            cursor.execute(transactions_per_second)
            result = cursor.fetchall()
            # print(result)
            state_list.append(float(result[0][0]))

            # 扫描、更新、删除行
            cursor.execute(tup)
            result = cursor.fetchall()
            for i in result[0]:
                state_list.append(float(i))

            cursor.close()
            conn.close()
        except Exception as error:
            print(error)
        for i in range(len(state_list)):
            state_list[i] = float(state_list[i])
        return state_list

    def fetch_knob(self):
        state_list = []
        conn = self.get_conn()
        cursor = conn.cursor()
        for n in self.knob_names:
            sql = "SELECT name, setting FROM pg_settings WHERE name={}".format(n)
            cursor.execute(sql)
            result = cursor.fetchall()
            for s in result:
                state_list = np.append(state_list, s[1])
        print(len(state_list))
        return state_list

    def max_connections(self):
        if self.max_connections_num:
            return self.max_connections_num
        try:
            conn = self.get_conn()
            cursor = conn.cursor()
            sql = "SELECT name, max_val FROM pg_settings WHERE name='max_connections';"
            cursor.execute(sql)
            self.max_connections_num = int(cursor.fetchone()[1])
            cursor.close()
            conn.close()
        except Exception as error:
            print('get max_connections error: {}'.format(error))
        return self.max_connections_num

    def change_knob_non_restart(self, actions):
        for i in range(self.knob_num):
            name = self.knob_names[i]
            value = actions[i]
            name = name[1:]
            name = name[:-1]
            try:
                self.ssh.exec_command(
                    "gs_guc reload -c \"%s=%s\" -D /home/omm/huawei/install/data/dn" % (name, int(value)))
            except Exception as e:
                if str(e).find('Success to perform gs_guc!') == 0:
                    logging.warning(e)
                    return False
        return True


# Define the environment
class Environment(gym.Env, ABC):

    def __init__(self, db, predictor):

        self.db = db

        self.predictor = None

        self.state_num = self.db.internal_metric_num
        self.action_num = self.db.knob_num
        self.timestamp = int(time.time())

        self.score = 0  # accumulate rewards
        # o_dim: observation
        self.o_dim = self.db.internal_metric_num
        self.o_low = np.array([-1e+10] * self.o_dim)
        self.o_high = np.array([1e+10] * self.o_dim)

        self.observation_space = spaces.Box(low=self.o_low, high=self.o_high, dtype=np.float32)
        self.state = self.db.fetch_inner_metric()

        # 是否使用predictor，同时修改get_obs
        # self.state = np.append(self.state, self.predictor.predict_inner_metric_change(self.workload))

        self.knob_num = len(db.knob_config)
        self.a_low = np.array([knob['min_val'] / knob['step'] for knob in self.db.knob_config])
        self.a_high = np.array([knob['max_val'] / knob['step'] for knob in self.db.knob_config])
        self.length = np.array([knob['step'] * 1.0 for knob in self.db.knob_config])
        self.action_space = spaces.Box(low=self.a_low, high=self.a_high, dtype=np.float32)
        self.default_action = np.array([knob['boot_val'] / knob['step'] for knob in self.db.knob_config])
        self.mem = deque(maxlen=int(self.db.database_config['maxlen_mem']))  # [throughput, latency]
        self.predicted_mem = deque(maxlen=int(self.db.database_config['maxlen_predict_mem']))
        # self.knob2pos = {knob: i for i, knob in enumerate(self.db.knob_config)}
        self.seed()
        self.start_time = datetime.datetime.now()

    def seed(self, seed=None):
        _, seed = seeding.np_random(seed)
        return [seed]

    def fetch_action(self):
        while True:
            state_list = self.db.fetch_knob()
            if list(state_list):
                break
            time.sleep(5)
        return state_list

    def test_by_sysbench(self):

        log_file = sys.path[0] + '/log/{}.log'.format(int(time.time()))

        command = 'sysbench --db-driver=pgsql --threads=64 --pgsql-host={} --pgsql-port={} --pgsql-user={} ' \
                  '--pgsql-password={} --pgsql-db={} --tables={} --table-size={} --time={} oltp_read_write run'.format(
            'localhost',  # self.host,
            15400,  # self.port,
            'tianjikun',  # self.user,
            'tianjikun123@',  # self.password,
            'tianjikun',  # self.db,
            50,  # self.tables,
            1000000,  # self.table_size,
            120, # self.runing_time
        )

        os.system(command + ' > {} '.format(log_file))

        tps = 0
        with open(log_file) as f:
            lines = f.readlines()
        for line in lines:
            if 'transaction' in line:
                tps = float(line.split()[1])
            else:
                tps = 0
            if '95th percentile' in line:
                lat = float(line.split()[2]) / 1000
            else:
                lat = 0
        print('tps = {}\tlat = {}'.format(tps, lat))
        return tps, lat

    # new_state, reward, done,
    def step(self, u, isPredicted, iteration, action_tmp=None):
        flag = self.db.change_knob_non_restart(u)

        # if failing to tune knobs, give a high panlty
        if not flag:
            print("error: change knob fail...")
            return self.state, -10e+4, self.score, 0

        # total_lat = self.execute_command()  # 执行负载测试knob，获取throughput和latency
        #
        # throughput, latency = self.get_throughput_latency()

        throughput, latency = self.test_by_sysbench()

        cur_time = datetime.datetime.now()
        interval = (cur_time - self.start_time).seconds
        self.mem.append([throughput, latency])
        # 2 state
        self.get_obs()
        # 3 cul reward(T, L)
        reward = self.calculate_reward(throughput, latency)

        action = self.fetch_action()

        if isPredicted:
            self.predicted_mem.append([len(self.predicted_mem), throughput, latency, reward])

            print("Predict %d\t%f\t%f\t%f\t%ds" % (len(self.mem) + 1, throughput, latency, reward, interval))

            pfs = open('training-results/res_predict-' + str(self.timestamp), 'a')
            pfs.write("%d\t%f\t%f\n" % (iteration, throughput, latency))
            pfs.close()

            fetch_knob = open('training-results/fetch_knob_predict-' + str(self.timestamp), 'a')
            fetch_knob.write(f"{str(iteration)}\t{str(list(action))}\n")
            fetch_knob.close()

            action_write = open('training-results/action_test_predict-' + str(self.timestamp), 'a')
            action_write.write(f"{str(iteration)}\t{str(list(u))}\n")
            action_write.write(f"{str(iteration)}\t{str(list(action_tmp))}\n")
            action_write.close()

            self.score = self.score + reward

        else:
            print("Random %d\t%f\t%f\t%f\t%ds" % (len(self.mem) + 1, throughput, latency, reward, interval))

            rfs = open('training-results/res_random-' + str(self.timestamp), 'a')
            rfs.write("%d\t%f\t%f\n" % (iteration, throughput, latency))
            rfs.close()

            action_write = open('training-results/action_random-' + str(self.timestamp), 'a')
            action_write.write(f"{str(iteration)}\t{str(list(u))}\n")
            action_write.close()

            fetch_knob = open('training-results/fetch_knob_random-' + str(self.timestamp), 'a')
            fetch_knob.write(f"{str(iteration)}\t{str(list(action))}\n")
            fetch_knob.close()

        return self.state, reward, self.score, throughput

    def get_throughput_latency(self):
        throughput, latency = 0, 0
        with open(self.db.database_config['run_job_result_file_path'], 'r') as f:
            try:
                for line in f.readlines():
                    a = line.split()
                    if len(a) > 1 and 'avg_qps(queries/s):' == a[0]:
                        throughput = float(a[1])
                    if len(a) > 1 and 'avg_lat(s):' == a[0]:
                        latency = float(a[1])
                    if throughput != 0 and latency != 0:
                        break
            finally:
                f.close()
            return throughput, latency

    def calculate_reward(self, throughput, latency):
        if len(self.mem) != 0:
            dt0 = (throughput - self.mem[0][0]) / self.mem[0][0]
            dt1 = (throughput - self.mem[len(self.mem) - 1][0]) / self.mem[len(self.mem) - 1][0]
            if dt0 >= 0:
                rt = ((1 + dt0) ** 2 - 1) * abs(1 + dt1)
            else:
                rt = -((1 - dt0) ** 2 - 1) * abs(1 - dt1)

            dl0 = -(latency - self.mem[0][1]) / self.mem[0][1]

            dl1 = -(latency - self.mem[len(self.mem) - 1][1]) / self.mem[len(self.mem) - 1][1]

            if dl0 >= 0:
                rl = ((1 + dl0) ** 2 - 1) * abs(1 + dl1)
            else:
                rl = -((1 - dl0) ** 2 - 1) * abs(1 - dl1)

        else:  # initial action
            rt = 0
            rl = 0
        reward = 1 * rl + 9 * rt
        return reward

    def get_obs(self):
        self.state = np.array(self.db.fetch_inner_metric())  # (65,)
        # print(self.state.shape)
        # 是否使用predictor
        # self.state = np.append(self.state, self.predictor.predict_inner_metric_change(self.workload))
        # print(self.state.shape)
        return self.state
