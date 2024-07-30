import os
import threading
import time
from configs import parse_args

args = parse_args()
lock = threading.Lock()
total_lat = 0
error_query_num = 0

POOL = None


# 把任务放入队列中
class Producer(threading.Thread):
    def __init__(self, name, queue, workload):
        self.__name = name
        self.__queue = queue
        self.workload = workload
        super(Producer, self).__init__()

    def run(self):
        for index, query in enumerate(self.workload):
            self.__queue.put(str(index) + "~#~" + query)


# 线程处理任务
class Consumer(threading.Thread):
    def __init__(self, name, queue):
        self.__name = name
        self.__queue = queue
        super(Consumer, self).__init__()

    def run(self):
        while not self.__queue.empty():
            query = self.__queue.get()
            try:
                consumer_process(query)
            finally:
                self.__queue.task_done()


def consumer_process(task_key):
    query = task_key.split('~#~')[1]
    if query:

        start = time.time()
        result = mysql_query(query)
        end = time.time()
        interval = end - start

        if result:
            lock.acquire()
            global total_lat
            total_lat += interval
            lock.release()

        else:
            global error_query_num
            lock.acquire()
            error_query_num += 1
            lock.release()


def startConsumer(thread_num, queue):
    t_consumer = []
    for i in range(thread_num):
        c = Consumer(i, queue)
        c.setDaemon(True)
        c.start()
        t_consumer.append(c)
    return t_consumer


def run_job(thread_num=1, workload=[], resfile="../output.res"):
    command_run = 'sysbench --db-driver=mysql --threads={} --mysql-host={} --mysql-port={} --mysql-user={} --mysql-password={} --mysql-db={} --tables={} --table-size={} --time={} --report-interval=60 oltp_read_write run'.format(
        args['sb_thread'],
        args['host'],
        args['port'],
        args['user'],
        args['password'],
        args['database'],
        args['sb_tables'],
        args['sb_table_size'],
        args['sb_time']
    )
    head_command = 'sshpass -p {} ssh {} '.format(args['ssh_pwd'], args['ssh_host'])
    command_run = head_command + '"' + command_run + '"'
    out = os.popen(command_run)
    res = out.readlines()
    qps = 0
    lat = 0
    for l in res:
        if 'queries:' in l:
            qps = float(l.split()[2][1:])
        if '95th percentile:' in l:
            lat = float(l.split()[2])
    return qps, lat

    # return round(avg_qps, 4), round(avg_lat, 4)


def mysql_query(sql: str) -> bool:
    try:
        global POOL
        conn = POOL.connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.close()
        conn.commit()
        return True
    except Exception as error:
        print("mysql execute: " + str(error))
        return False
