import random

import keras
import numpy as np
import tensorflow as tf
import keras.backend as K

from configs import parse_args, get_workload, get_knob_config, set_workload
from environment import Database, Environment
from predictor import Predictor
from rl_model import ActorCritic

import csv


def run():
    argus = parse_args()
    sess = tf.Session()
    K.set_session(sess)
    db = Database()  # connector knobs metric
    predictor = Predictor()
    env = Environment(db, predictor)

    actor_critic = ActorCritic(env, sess, learning_rate=float(argus['database_tune']['learning_rate']),
                               train_min_size=int(argus['database_tune']['train_min_size']),
                               size_mem=int(argus['database_tune']['maxlen_mem']),
                               size_predict_mem=int(argus['database_tune']['maxlen_predict_mem']))

    actor_critic.actor_model.load_weights(r'ddpg_model_weights/actor_weights.h5')
    actor_critic.critic_model.load_weights(r'ddpg_model_weights/critic_weights.h5')

    num_trials = int(argus['database_tune']['num_trial'])

    # First iteration
    cur_state = env.get_obs()  # np.array [inner_metric change after execute sql, inner_metric]
    cur_state = cur_state.reshape((1, env.state.shape[0]))
    # action = env.action_space.sample()
    action = env.fetch_action()  # np.array
    action_2 = action.reshape((1, env.knob_num))  # for memory
    action_2 = action_2[:, :env.action_space.shape[0]]

    # action_boot = [42.0, 5108490.0, 1066130.0, 52.0, 42.0, 5620450.0, 124.0, 127.0, 510.0, 4745.0, 861315072.0, 537.0,
    #                901907584.0, 1030800896.0, 3250.0, 5250784.0, 1142039424.0, 3765.0, 5068.0, 4530.0, 5298.0, 4410.0,
    #                1196035072.0]
    # action_boot = []
    # knobs = get_knob_config()
    # for knob in knobs:
    #     action_boot.append(float(knob['boot_val']))
    # env.db.change_knob_non_restart(action_boot)
    #
    # ns, rw, sc, cth, lat = env.step(action_boot, 0, 1)
    #
    # print("%%%%%%%%%%%%{}".format(cth))

    new_state, reward, score, cur_throughput, total_lat = env.step(action, 0, 1)
    new_state = new_state.reshape((1, env.state.shape[0]))
    reward_np = np.array([reward])
    print(reward_np)
    actor_critic.remember(cur_state, action_2, reward_np, new_state, False)
    actor_critic.train(1)  # len<[train_min_size], useless

    cur_state = new_state
    predicted_rewardList = []
    best_throughput = 0
    metric_knob = []
    for epoch in range(num_trials):
        # env.render()
        cur_state = cur_state.reshape((1, env.state.shape[0]))
        action, isPredicted, action_tmp = actor_critic.act(cur_state)
        # action.tolist()                                          # to execute
        new_state, reward, score, throughput, total_lat = env.step(action, isPredicted, epoch + 1, action_tmp)
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

        if best_throughput < throughput:
            best_throughput = throughput
            state = [i for i in cur_state[0]]
            knob = [i for i in action_2[0]]
            state = np.array(state)
            knob = np.array(knob)
            metric_knob = [state, knob]
            metric_knob = np.array(metric_knob)

        actor_critic.remember(cur_state, action_2, reward_np, new_state, False)
        actor_critic.train(epoch)

        cur_state = new_state

    for index, tmp in enumerate(metric_knob[0]):
        metric_knob[0][index] = float(tmp)

    k = 0
    while True:
        action, isPredicted, action_tmp = actor_critic.act(metric_knob[0].reshape((1, env.state.shape[0])))
        if isPredicted:
            continue
        if k == 5:
            break
        new_state, reward, score, throughput, total_lat = env.step(action, isPredicted, epoch + 1, action_tmp)
        action = env.fetch_action()
        action_2 = action.reshape((1, env.knob_num))  # for memory
        action_2 = action_2[:, :env.action_space.shape[0]]
        knob = [i for i in action_2[0]]
        for index, tmp in enumerate(knob):
            knob[index] = float(tmp)
        ss = [i for i in metric_knob[0]]
        with open('samples23.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ss, knob, throughput, total_lat / 10000])
            writer.writerow("\n")

        k = k + 1


for i in range(10):
    set_workload(i + 1)
    run()
