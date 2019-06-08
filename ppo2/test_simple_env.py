#!/usr/bin/env python3
import sys
from baselines import logger
from baselines.common.cmd_util import make_atari_env, atari_arg_parser
from baselines.common.vec_env.vec_frame_stack import VecFrameStack
from baselines.ppo2 import ppo2
from baselines.ppo2.policies import CnnPolicy, LstmPolicy, LnLstmPolicy, MlpPolicy
import multiprocessing
import tensorflow as tf
import gym


def train(env_id, num_timesteps, seed, policy):

    # 首先是和TensorFlow相关的环境设置，比如根据cpu核数设定并行线程数等
    ncpu = multiprocessing.cpu_count()
    if sys.platform == 'darwin': ncpu //= 2  # 4
    config = tf.ConfigProto(allow_soft_placement=True,
                            intra_op_parallelism_threads=ncpu,
                            inter_op_parallelism_threads=ncpu)
    config.gpu_options.allow_growth = True  # pylint: disable=E1101
    tf.Session(config=config).__enter__()

    env = gym.make("CartPole-v0")
    # env = VecFrameStack(make_atari_env(env_id, 8, seed), 4)
    policy = {'cnn': CnnPolicy, 'lstm': LstmPolicy, 'lnlstm': LnLstmPolicy, 'mlp': MlpPolicy}[policy]
    ppo2.learn(policy=policy, env=env, nsteps=128, nminibatches=4,
               lam=0.95, gamma=0.99, noptepochs=4, log_interval=1,
               ent_coef=.01, lr=lambda f: f * 2.5e-4,
               cliprange=lambda f: f * 0.1,
               total_timesteps=int(num_timesteps * 1.1))


def main():
    parser = atari_arg_parser()
    parser.add_argument('--policy', help='Policy architecture', choices=['cnn', 'lstm', 'lnlstm', 'mlp'], default='cnn')
    args = parser.parse_args()
    # 这个项目中实现了简单的日志系统,其中日志所在目录和格式可以用过OPENAI_LOGDIR和OPENAI_LOG_FORMAT两个环境
    # 变量控制,实现类Logger中主要有两个字典：name2val和name2cnt。它们分别是名称到值和计数的映射。
    logger.configure()
    train(args.env, num_timesteps=args.num_timesteps, seed=args.seed,
        policy=args.policy)


if __name__ == '__main__':
    main()