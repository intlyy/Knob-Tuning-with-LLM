import utils
import config
import json
import itertools
import pandas as pd
from pyDOE import lhs
import numpy as np
import sys
import os
import time
from stress_testing_tool import stress_testing_tool
from poap.controller import BasicWorkerThread, ThreadController
from pySOT.experimental_design import LatinHypercube
from pySOT import strategy, surrogate
from ConfigSpace import ConfigurationSpace, Integer
from smac import HyperparameterOptimizationFacade as HPOFacade
from smac import Scenario
from smac.initial_design import LatinHypercubeInitialDesign
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
from scipy.stats import norm
from bayes_opt import BayesianOptimization
import tensorflow as tf
import keras.backend as K
from environment import Database, Environment
from rl_model import ActorCritic
from configs import parse_args, get_workload

class tuner:
    def __init__(self):
        self.method = config.method
        self.iteration = config.iteration
        self.knobs_number = config.knobs_number
        self.sampling_number = config.sampling_number
        self.knobs_detail = utils.get_knobs_detail()
        self.benchmark = config.benchmark
        self.predictor = config.predictor

        self.id = int(time.time())
        #self.id = 111
        self.file_path = './history_results/{}'.format(self.id)
        self.log_file = './history_results/{}/log'.format(self.id)
        os.mkdir(self.file_path)
        os.mkdir(self.log_file)
        os.system('cp ./config.py ./history_results/{}'.format(self.id))

        self.logger = utils.get_logger(self.file_path)
        self.stt = stress_testing_tool(self.logger,self.knobs_detail,self.id)

    def tune(self):

        if self.method == 'SMAC':
            self.SMAC()
        elif self.method == 'VBO':
            #self.LHS()
            self.VBO()
        elif self.method == 'TEST':
            self.LHS()
        elif self.method == 'DDPG'
            self.DDPG()
        #self.test_best_config()
    
    def LHS(self):
        if self.sampling_number == 0:
            return
        
        lb,ub = [],[]
        for index,knob in enumerate(self.knobs_detail):
            if self.knobs_detail[knob]['type'] == 'integer':
                lb.append(int(self.knobs_detail[knob]['min']))
                ub.append(int(self.knobs_detail[knob]['max']))
            elif self.knobs_detail[knob]['type'] == 'enum':
                lb.append(0)
                ub.append(len(self.knobs_detail[knob]['enum_values']) - 1)
        
        lb = np.array(lb)
        ub = np.array(ub)
        points_dict = []
        points = (lb + (ub-lb) * lhs(self.knobs_number,self.sampling_number)).astype(int).tolist()
        for point in points:
            temp = {}
            for index,knob in enumerate(self.knobs_detail):
                if index == self.knobs_number:
                    break
                temp[knob] = point[index]

            points_dict.append(temp)
        
        for point in points_dict:
            self.stt.test_config(point)
    
    
    
    def SMAC(self):
        params = {}
        print("TEST!!!")
        print(self.knobs_detail)
        for name in self.knobs_detail.keys():
            if self.knobs_detail[name]['type'] == "integer":
                if int(self.knobs_detail[name]['max']) > sys.maxsize:
                    params[name] = Integer(name,bounds=(int(int(self.knobs_detail[name]['min']) / 10000),int(int(self.knobs_detail[name]['max']) / 10000)))
                else:
                    params[name] = Integer(name,bounds=(int(self.knobs_detail[name]['min']),int(self.knobs_detail[name]['max'])))
            elif self.knobs_detail[name]['type'] == "enum":
                params[name] = Integer(name,bounds=(0,len(self.knobs_detail[name]['enum_values']) - 1))

        configspace = ConfigurationSpace(seed=0,space=params)
        scenario = Scenario(configspace, deterministic=True, n_trials=self.iteration+self.sampling_number)

    
        smac = HPOFacade(
            scenario,
            self.stt.handle_SMAC_config,
            overwrite=True,  # Overrides any previous results that are found that are inconsistent with the meta-data
            initial_design=LatinHypercubeInitialDesign(scenario,max_ratio=1,n_configs=self.sampling_number)
        )
        
        smac.optimize()
        
    def VBO(self):
        '''params_list = []
        for name in self.knobs_detail.keys():
            if len(params_list) == 0:
                params_list = list(range(self.knobs_detail[name]['min'],self.knobs_detail[name]['max']))
            else:
                params_list = list(itertools.product(params_list,list(range(self.knobs_detail[name]['min'],self.knobs_detail[name]['max']))))

        params_list = np.array(params_list)
        kernel = RBF(length_scale=1.0)
        gp_model = GaussianProcessRegressor(kernel=kernel)

        init_num = 111
        with open('./history_results/{}/records'.format(init_num),'r') as f:
            lines = f.readlines()[:]

        knobs = []
        qps = []
        record = [] #记录采样过程中最后一次成功运行的配置的记录
        for line in lines:
            knobs.append(json.loads(line)['knobs'])
            qps.append(json.loads(line)['qps'])
            if len(json.loads(line)['metrics']) > 0:
                record = json.loads(line)

        denied_times = 0
        success_times = 0
        #for step in range(self.iteration):
        while success_times < self.iteration :
            gp_model.fit(np.array(knobs).reshape(-1, 1), qps)
            ei = self.expected_improvement(params_list,gp_model,max(qps))
            df = pd.DataFrame(params_list,self.knobs_detail.keys())
            df['ei'] = ei
            df = df.sort_values(by='ei',ascending=False).reset_index()
            rec_x = np.array(df.iloc[:-1,denied_times])

            if self.predictor == 1 and denied_times <= 5:
                knobs_sug = {}
                rec_x = rec_x.reset_index(drop=True)

                for key in self.knobs_detail.keys():
                    knobs_sug[key] = int(rec_x.loc[0,key])
        
                if utils.safe_check(record['metrics'],record['knobs'],knobs_sug) > 0.5:
                    success_times += 1
                    tmp = self.stt.handle_VBO_config(rec_x) 
                    knobs.append(tmp['metrics'])
                    qps.append(tmp['qps'])
                    if len(tmp['metrics']) > 0 :
                        record = tmp

                else:
                    self.logger.info('predictor denied')

                    #qps = [0]
                    #hebo_batch.observe(rec_x, np.array(qps))
                    denied_times += 1
                    continue
            else:
                denied_times = 0
                success_times += 1
                tmp = self.stt.handle_VBO_config(rec_x) 
                knobs.append(tmp['metrics'])
                qps.append(tmp['qps'])
                if len(tmp['metrics']) > 0 :
                        record = tmp'''
        params = {}
        for name in self.knobs_detail.keys():
            if self.knobs_detail[name]['type'] == "integer":
                params[name] = (int(self.knobs_detail[name]['min']),int(self.knobs_detail[name]['max']))
            elif self.knobs_detail[name]['type'] == "enum":
                params[name] = (0,len(self.knobs_detail[name]['enum_values']) - 1)

        optimizer = BayesianOptimization(f=self.stt.handle_VBO_config,pbounds=params,random_state=1)

        # with open('/home/puzhao/opengauss_tuning/transfer/configuration/llama70B', 'r') as f:
        #     data = json.load(f)

        # # Prepare the final structured JSON format
        # formatted_data = []
        # for  d in data:
        #     formatted_entry = {
        #         'knob': d,
        #         'qps': 0
        #     }
        #     formatted_data.append(formatted_entry)

        # # Convert to JSON string
        # json_output = json.dumps(formatted_data, indent=4)

        # # Print or save the JSON as needed
        # print(json_output)

        # with open('/home/puzhao/opengauss_tuning/transfer/history_llama8B.json', 'r') as file:
        #     history_data = json.load(file)

        #测试历史数据
        with open('/home/puzhao/opengauss_tuning/transfer/configuration/qianwen2', 'r') as f:
            data_str = f.read()

        # Split the data into individual JSON strings
        json_strings = data_str.strip().split('\n')
        num_items = len(json_strings)
        print(f"Load Data!: {num_items}")
        # Prepare the final structured JSON format
        for json_str in json_strings:
            d = json.loads(json_str)
            #print(d)
            temp_config = {}
            knobs_detail = self.knobs_detail
            for key in knobs_detail.keys():
                    if knobs_detail[key]['type'] == 'integer':
                        temp_config[key] = d.get(key) 
                    elif knobs_detail[key]['type'] == 'enum':
                        temp_config[key] = knobs_detail[key]['enum_values'][d.get(key)]
            print(temp_config)
            self.stt.test_config(temp_config)
        
       
        # 加载历史数据
        with open('./history_results/{}/records'.format(self.id),'r') as file:
            history_data = file.readlines()

        for l in history_data:
            data_point = json.loads(l)
            optimizer.register(params=data_point['knobs'], target=-float(data_point['qps']))
            print(data_point['knobs'])
            print(-float(data_point['qps']))

        # with open('/home/puzhao/opengauss_tuning/history_results/1720798698/records','r') as file:
        #     history_data = file.readlines()

        # for l in history_data:
        #     data_point = json.loads(l)
        #     optimizer.register(params=data_point['knobs'], target=-float(data_point['qps']))
        #     print(data_point['knobs'])
        #     print(-float(data_point['qps']))
        
        
        
        print("Success Laod Data!")

        optimizer.maximize(init_points=self.sampling_number,n_iter=self.iteration)
    
    def DDPG(self):
        argus = parse_args()
        # workload = get_workload()
        sess = tf.Session()
        K.set_session(sess)
        db = Database()  # connector knobs metric
        # predictor = Predictor()
        predictor = None
        # predictor.train_predictor(workload, 10)
        env = Environment(db, predictor)

        actor_critic = ActorCritic(env, sess, learning_rate=float(argus['database_tune']['learning_rate']),
                                train_min_size=int(argus['database_tune']['train_min_size']),
                                size_mem=int(argus['database_tune']['maxlen_mem']),
                                size_predict_mem=int(argus['database_tune']['maxlen_predict_mem']))

        num_trials = int(argus['database_tune']['num_trial'])

        # First iteration
        cur_state = env.get_obs()  # np.array [inner_metric change after execute sql, inner_metric]
        cur_state = cur_state.reshape((1, env.state.shape[0]))
        # action = env.action_space.sample()
        action = env.fetch_action()  # np.array
        action_2 = action.reshape((1, env.knob_num))  # for memory
        action_2 = action_2[:, :env.action_space.shape[0]]
        new_state, reward, score, cur_throughput= env.step(action, 0, 1)
        new_state = new_state.reshape((1, env.state.shape[0]))
        reward_np = np.array([reward])
        print(reward_np)
        actor_critic.remember(cur_state, action_2, reward_np, new_state, False)
        actor_critic.train(1)  # len<[train_min_size], useless

        cur_state = new_state
        predicted_rewardList = []
        best_throughput = 0
        for epoch in range(num_trials):
            # env.render()
            print('==========epoch: {}============'.format(epoch))
            cur_state = cur_state.reshape((1, env.state.shape[0]))
            action, isPredicted, action_tmp = actor_critic.act(cur_state)
            # action.tolist()                                          # to execute
            new_state, reward, score, throughput = env.step(action, isPredicted, epoch + 1, action_tmp)
            new_state = new_state.reshape((1, env.state.shape[0]))

            action = env.fetch_action()
            action_2 = action.reshape((1, env.knob_num))  # for memory
            action_2 = action_2[:, :env.action_space.shape[0]]

            if isPredicted == 1:
                predicted_rewardList.append([epoch, reward])
                print("[predicted]", action_2, reward, throughput)
            else:
                print("[random]", action_2, reward, throughput)

            reward_np = np.array([reward])

            # remember in files
            with open('samples19.csv', 'a', newline='') as f:
                writer = csv.writer(f)

                tmp = list()
                for i in cur_state[0]:
                    tmp.append(float(i))
                cur_state = [tmp]
                cur_state = np.array(cur_state)

                tmp = list()
                for i in new_state[0]:
                    tmp.append(float(i))
                new_state = [tmp]
                new_state = np.array(new_state)

                writer.writerow([cur_state, action_2, throughput])
                writer.writerow("\n")

            actor_critic.remember(cur_state, action_2, reward_np, new_state, False)
            actor_critic.train(epoch)

            # if cur_throughput > best_throughput:
            #     best_throughput = cur_throughput
            #     actor_critic.actor_model.save_weights('ddpg_model_weights/actor_weights.h5')
            #     actor_critic.critic_model.save_weights('ddpg_model_weights/critic_weights.h5')

            # print('============train running==========')

            # if epoch % 5 == 0:
            #     # print('============save_weights==========')
            #     actor_critic.actor_model.save_weights('saved_model_weights/actor_weights.h5')
            #     actor_critic.critic_model.save_weights('saved_model_weights/critic_weights.h5')
            '''
            if (throughput - cur_throughput) / cur_throughput > float(argus['stopping_throughput_improvement_percentage']):
                print("training end!!")
                env.parser.close_mysql_conn()
                break
            '''

            cur_state = new_state

    def test_best_config(self):
        data=utils.load_sampling_data('./history_results/{}/records'.format(self.id))
        best_config = data.iloc[data['qps'].idxmin()].to_dict()
        del best_config['qps']

        self.stt.test_config(best_config)
        self.stt.test_config(best_config)

        random_config = data.iloc[250].to_dict()
        del random_config['qps']

        self.stt.test_config(random_config)
        self.stt.test_config(random_config)

    def expected_improvement(x, gp_model, best_y):
        y_pred, y_std = gp_model.predict(x.reshape(-1, 1), return_std=True)
        z = (y_pred - best_y) / y_std
        ei = (y_pred - best_y) * norm.cdf(z) + y_std * norm.pdf(z)
        return ei