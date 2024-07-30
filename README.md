# Is Large Language Model Good at Database Konb Tuning? A Comprehensive Experimental Evaluation

This is the source code to the paper "Is Large Language Model Good at Database Konb Tuning? A Comprehensive Experimental Evaluation". Please refer to the paper for the experimental details.

## Table of Content




* [Environment Installation](https://github.com/intlyy/Knob-Tuning-with-LLM#environment-installation)
* [Workload Preparation](https://github.com/intlyy/Knob-Tuning-with-LLM#workload-preparation)
* [Exp.1: Knob Pruning.](https://github.com/intlyy/Knob-Tuning-with-LLM#exp1-knob-pruning)
* [Exp.2: Model Initialization.](https://github.com/intlyy/Knob-Tuning-with-LLM#exp2-model-initialization)
* [Exp.3: Knob Recommendation.](https://github.com/intlyy/Knob-Tuning-with-LLM#exp3-knob-recommendation)
* [Exp.4: Generalization.](https://github.com/intlyy/Knob-Tuning-with-LLM#exp4-generalization)



  



 


## Environment Installation

In our experiments,  We conduct experimets on MySQL 5.7.

1. Preparations: Python == 3.7

2. Install packages

   ```shell
   pip install -r requirements.txt
   pip install .
   ```

3. Download and install MySQL 5.7 and boost

   ```shell
   wget http://sourceforge.net/projects/boost/files/boost/1.59.0/boost_1_59_0.tar.gz
   wget https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-boost-5.7.19.tar.gz
   
   sudo cmake . -DCMAKE_INSTALL_PREFIX=PATH_TO_INSTALL -DMYSQL_DATADIR=PATH_TO_DATA -DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci -DMYSQL_TCP_PORT=3306 -DWITH_MYISAM_STORAGE_ENGINE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 -DWITH_ARCHIVE_STORAGE_ENGINE=1 -DWITH_BLACKHOLE_STORAGE_ENGINE=1 -DWITH_MEMORY_STORAGE_ENGINE=1 -DENABLE_DOWNLOADS=1 -DDOWNLOAD_BOOST=1 -DWITH_BOOST=PATH_TO_BOOST;
   sudo make -j 16;
   sudo make install;
   ```



## Workload Preparation 

### SYSBENCH

Download and install

```shell
git clone https://github.com/akopytov/sysbench.git
./autogen.sh
./configure
make && make install
```

Load data

```shell
sysbench --db-driver=mysql --mysql-host=$HOST --mysql-socket=$SOCK --mysql-port=$MYSQL_PORT --mysql-user=root --mysql-password=$PASSWD --mysql-db=sbtest --table_size=800000 --tables=150 --events=0 --threads=32 oltp_read_write prepare > sysbench_prepare.out
```

### Join-Order-Benchmark (JOB)

Download IMDB Data Set from http://homepages.cwi.nl/~boncz/job/imdb.tgz.

Follow the instructions of https://github.com/winkyao/join-order-benchmark to load data into MySQL.







## Exp.1: Knob Pruning

Compared importance measurements:  `shap`, `Expert`, `GPT-4`, `GPT-4o`, `GPT-3.5`, `Claude`, `Llama3-8B`, `Llama3-70B`, `Qwen2-7B`.

To conduct the experiment shown in Figure 4, the script is as follows. 

1. modify  `/Tuning_framework/config.py`, where
   - `method` = 'SMAC'
   - `knobs_file` = Path to selected knobs file
    Knobs we selected with the above methods are all saved in the `/Tuning_framework/knobs_config`
   - `benchmark` = 'sysbench'
   - database configs, including `port`, `host`, `db_user`, `db_password`, `database`, `ip_address`, `ip_password`, and `database configuration file path`
   - sysbench configs, including tables, table_size, runing_time, warm_up_time, and threads

2. run
   ```shell
   cd /Tuning_framework
   ./run.sh
   ```
   Results in `/Tuning_framework/history_results`

For generating knob list with other LLMs, modify `Select.py` in `/Exp1_Knob_Pruning ` and then
   ```shell
   cd /Exp1_Knob_Pruning
   python Select.py
   ```

## Exp.2: Model Initialization 

To conduct the experiment shown in Table 2, the script is as follows.

1. generate initial data points via LLMs
   - modify   `transfer.py` in `/Exp2_Model_Initialization` , fill the model you want to use and the corresponding API-Key in
    ```python
      model = ""
      client = OpenAI(
          base_url=,
          api_key="",
      )
    ```
  - Execute `transfer.py` and `check_knob.py` in turn to obtain the initial points and remove improperly formatted data.
     ```shell
      cd /Exp2_Model_Initialization
      python transfer.py
      python check_knob.py
    ```
   You can also ues the initial points we generated in  `/Tuning_framework/transfer/configuration`.

2. modify  `/Tuning_framework/config.py`, where
   - `method` = 'VBO'
   - `knobs_file` = './knobs_config/knobs-transfer.json'
   - `benchmark` = 'sysbench'
   - database configs, including `port`, `host`, `db_user`, `db_password`, `database`, `ip_address`, `ip_password`, and `database configuration file path`
   - sysbench configs, including tables, table_size, runing_time, warm_up_time, and threads
   - sampling_number = 0
   - transfer = 'YES'
   - Data_dir = Path to initial points

3. run
  ```shell
  cd /Tuning_framework
  ./run.sh
  ```
  Results in `/Tuning_framework/history_results`

## Exp.3: Knob Recommendation

To conduct the experiment shown in Table 3, the script is as follows.

1. execute LLM server
    - modify   `openai_server.py` in `/Exp3_Knob_Recommendation` fill the model you want to use and the corresponding API-Key in
    ```python
      model = ""
      client = OpenAI(
          base_url=,
          api_key="",
      )
    ```
    and select port in 
    ```python
      app.run(host='0.0.0.0', port=5000)
    ```
    
   - run
    ```shell
    cd /Exp3_Knob_Recommendation
    nohup python -u openai_server.py >out.log 2>&1 &
    ```

2. tuning with LLM
   - modify   `call_openai.py` in `/Exp3_Knob_Recommendation` fill the database information in 
    ```python
      mysql_ip = 
      ip_password = ''
      config = {
          'user': '',      
          'password': '',   
          'host': '',           
          'database': 'sysbench',   
          'port': 3306
      }
    ```
    and LLM server url 
    ```python
     url = ''
    ```
   - tune
   ```shell
    nohup python -u call_openai.py 2>&1 &
   ```

## Exp.4: Generalization

To conduct the experiment shown in Table 4 - 6, the script is as follows.

1. execute LLM server
    - modify  `{name}.py` in `/Exp4_Generalization`, fill the model you want to use and the corresponding API-Key in
    ```python
      model = ""
      client = OpenAI(
          base_url=,
          api_key="",
      )
    ```
    and select port in 
    ```python
       app.run(host='0.0.0.0', port=5000)
    ```
    
   - run
    ```shell
    cd /Exp4_Generalization
    nohup python -u {name}.py >out.log 2>&1 &
    ```
    Please replace `{name}` with 
      - `recommand_instanceB.py` : for Table4
      - `recommand_pg.py` and `recommand_tidb.py` : for Table5
      - `recommand_OLAP.py`: for Table6 

2. tuning with LLM
   - modify   `call_openai.py` in `/Exp4_Generalization` fill the database information in 
    ```python
      mysql_ip = 
      ip_password = ''
      config = {
          'user': '',      
          'password': '',   
          'host': '',           
          'database': 'sysbench',   
          'port': 3306
      }
    ```
    and LLM server url 
    ```python
     url = ''
    ```
   - tune
   ```shell
    nohup python -u call_openai.py 2>&1 &
   ```
