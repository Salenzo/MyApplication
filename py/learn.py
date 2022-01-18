import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import gym

# 项目参数（超参数）
BATCH_SIZE = 32               # 随机抽取BATCH_SIZE条数据。
LR = 0.01                     # 学习率 （learning rate）
EPSILON = 0.9                 # # 最优选择动作百分比 （greedy policy）
GAMMA = 0.9                   # 奖励递减参数 （reward discount）
TARGET_REPLACE_ITER = 100     # Q 现实网络的更新频率 （target update frequency）
MEMORY_CAPACITY = 2000        # 记忆库大小
env = gym.make('CartPole-v0') # 导入模拟实验,创建一个实验环境
env = env.unwrapped           # 还原env的原始配置， if 不还原就会限制step的次数(<200) 还原后就不受限制了
N_ACTIONS = env.action_space.n  # 杆子能做的动作 # 查看这个环境中可用的action有多少个，返回int
N_STATES = env.observation_space.shape[0] # 杆子能获取的环境信息数 #查看这个环境中observation的特征有多少个，返回int
ENV_A_SHAPE = 0 if isinstance(env.action_space.sample(), int) else env.action_space.sample().shape     # to confirm the shape

# 定义神经网络class
class Net(nn.Module):
    def __init__(self, ):
        super(Net, self).__init__()
        # 这里以一个动作为作为观测值进行输入，然后把他们输出给50个神经元
        # N_STATES 与 图像的特征值个数有关
        self.fc1 = nn.Linear(N_STATES, 50)
        # N_ACTIONS 与 能做的动作个数有关
        self.fc1.weight.data.normal_(0, 0.1)   # 初始化权重，用二值分布来随机生成参数的值
        # 经过50个神经元运算过后的数据， 把每个动作的价值作为输出。
        #
        self.out = nn.Linear(50, N_ACTIONS)    # 做出每个动作后，每个动作的价值作为输出。
        self.out.weight.data.normal_(0, 0.1)   # 初始化权重，用二值分布来随机生成参数的值
        # 输入-当前状态 action --Net网络--输出--》 所有动作价值
    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        actions_value = self.out(x)
        return actions_value

net = Net()
# 定义DQN 网络class
class DQN(object):
    def __init__(self):
        # 建立一个评估网络（eaval） 和 Q现实网络 （target）
        self.eval_net, self.target_net = Net(), Net()
        # 用来记录学习到第几步了
        self.learn_step_counter = 0                                     # for target updating
        # 用来记录当前指到数据库的第几个数据了
        self.memory_counter = 0                                         # for storing memory
        # MEMORY_CAPACITY = 2000 ， 限制了数据库只能记住2000个。前面的会被后面的覆盖
        # 一次存储的数据量有多大   MEMORY_CAPACITY 确定了memory数据库有多大 ，  后面的 N_STATES * 2 + 2 是因为 两个 N_STATES（在这里是4格子，因为N_STATES就为4）  + 一个 action动作（1格） + 一个 rward（奖励）
        self.memory = np.zeros((MEMORY_CAPACITY, N_STATES * 2 + 2))     # initialize memory
        # 优化器，优化评估神经网络（仅优化eval）
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=LR)
        self.loss_func = nn.MSELoss()
    # 进行选择动作
    def choose_action(self, x):
        # 获取输入
        x = torch.unsqueeze(torch.FloatTensor(x), 0)
        # input only one sample
        # 在大部分情况，我们选择 去max-value
        if np.random.uniform() < EPSILON:   # greedy # 随机结果是否大于EPSILON（0.9）
            actions_value = self.eval_net.forward(x) # if 取max方法选择执行动作
            action = torch.max(actions_value, 1)[1].data.numpy()
            action = action[0] if ENV_A_SHAPE == 0 else action.reshape(ENV_A_SHAPE)  # return the argmax index
        # 在少部分情况，我们选择 随机选择 （变异）
        else:   # random   # not if 取随机方法执行动作。
            action = np.random.randint(0, N_ACTIONS)
            action = action if ENV_A_SHAPE == 0 else action.reshape(ENV_A_SHAPE)
        # 输入动作action
        return action

    # 存储数据
    # 本次状态，执行的动作，获得的奖励分， 完成动作后产生的下一个状态。
    # 存储这四个值
    def store_transition(self, s, a, r, s_):
        # 把所有的记忆捆在一起，以 np类型
        # 把 三个矩阵 s ,[a,r] ,s_  平铺在一行 [a,r]是因为 他们都是 int 没有 [] 就无法平铺 ，并不代表把他们捆在一起了
        transition = np.hstack((s, [a, r], s_))
        # index 是 这一次录入的数据在 3000 的哪一个位置
        index = self.memory_counter % MEMORY_CAPACITY
        # 如果，记忆超过上线，我们重新索引。即覆盖老的记忆。
        self.memory[index, :] = transition
        self.memory_counter += 1
    # 从存储学习数据
    #  target 是 达到次数后更新， eval net是 每次learn 就进行更新
    def learn(self):
        # target parameter update  是否要更新现实网络
        # target Q现实网络 要间隔多少步跟新一下。 如果learn步数 达到 TARGET_REPLACE_ITER  就进行一次更新
        if self.learn_step_counter % TARGET_REPLACE_ITER == 0:
            # 把最新的eval 预测网络 推 给target Q现实网络
            # 也就是变成，还未变化的eval网
            self.target_net.load_state_dict(self.eval_net.state_dict()) # 把 eval的所有参数 赋值到 target中
        self.learn_step_counter += 1

        #  eval net是 每次learn 就进行更新
        #  更新逻辑就是从记忆库中随机抽取BATCH_SIZE个（32个）数据。
        sample_index = np.random.choice(MEMORY_CAPACITY, BATCH_SIZE)  # 从 数据库中 随机 抽取 BATCH_SIZE条数据
        b_memory = self.memory[sample_index, :] # 把这BATCH_SIZE个（32个）数据打包
        # 下面这些变量是 32个数据打包的变量
        b_s = torch.FloatTensor(b_memory[:, :N_STATES])  # 32个记忆的包，包里是（当时的状态）
        b_a = torch.LongTensor(b_memory[:, N_STATES:N_STATES+1].astype(int)) # 32个记忆的包，包里是（当时做出的动作）
        b_r = torch.FloatTensor(b_memory[:, N_STATES+1:N_STATES+2])  # 32个记忆的包，包里是 （当初获得的奖励）
        b_s_ = torch.FloatTensor(b_memory[:, -N_STATES:]) # 32个记忆的包，包里是 （执行动作后，下一个动作的状态）

        # q_eval w.r.t the action in experience
        # q_eval的学习过程
        # self.eval_net(b_s).gather(1, b_a)  输入我们包（32条）中的所有状态 并得到（32条）所有状态的所有动作价值， .gather(1,b_a) 只取这32个状态中 的 每一个状态的最大值
        # 预期价值计算 ==  随机32条数据中的最大值
        q_eval = self.eval_net(b_s).gather(1, b_a)  # shape (batch, 1)

        # 输入下一个状态 进入我们的现实网络 输出下一个动作的价值  .detach() 阻止网络反向传递，我们的target需要自己定义该如何更新，它的更新在learn那一步
        q_next = self.target_net(b_s_).detach()     # detach from graph, don't backpropagate
        # q_target 实际价值的计算  ==  当前价值 + GAMMA（未来价值递减参数） * 未来的价值
        q_target = b_r + GAMMA * q_next.max(1)[0].view(BATCH_SIZE, 1)   # shape (batch, 1)
        # q_eval预测值， q_target真实值
        loss = self.loss_func(q_eval, q_target)
        # 根据误差，去优化我们eval网
        # 因为这是eval的优化器
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()



# 运行总流程！！！

dqn = DQN()  # 实例化DQN类，也就是实例化这个强化学习网络
print('\nCollecting experience...')
# 进行2100次训练
for i_episode in range(2100):
    # 每一次新的训练
    # 开始，会重置我们的env， 每一次训练的环境都是独立的而完全一样的，只有网络记忆是一直留存的
    s = env.reset() # 获得初始化 observation 环境特征
    ep_r = 0  # 作为一个计数变量，来统计我第n次训练。 完成所有动作的分的总和

    # 开始实验循环
    # 只有env认为 这个实验死了，才会结束循环
    while True:
        env.render()  # 刷新环境状态  ， 使得screen 可以联系的动
        # 根据 输入的环境特征s  输出选择动作 a
        a = dqn.choose_action(s)
        # 通过当前选择的动作得到，执行这个动作后的结果也就是，下一步状态s_（也就是observation） 特征值矩阵  ，
        # 立即回报r 返回动作执行的奖励 ， r是一个float类型
        # 终止状态 done （done=True时环境结束） ， done 是 bool
        # 调试信息 info （一般没用）
        s_, r, done, info = env.step(a)    # env.step(a) 是执行 a 动作   它返回的就是 s_ ,r ,done , info
        # 到这里，预测流程就结束........

        # 下面是对预测的结果进行评价与修正.......
        # 因为 env.step(a)返回的rward难学，所以下面是对rward的规则进行调整，让训练时间短一点
	 # 方便理解，可以认为它还是r (返回执行动作的奖励)
        x, x_dot, theta, theta_dot = s_
        r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
        r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
        r = r1 + r2
        #####

        # 存储数据
        # 每完成一个动作，记忆存储数据一次
        dqn.store_transition(s, a, r, s_)

        # 最终得分 = 每一步得分 求合
        # 最后打印它，看这一次训练，最终得分是多少（可知道总分，但不知道执行了多少个动作，当然你也可以做一个计算器算一下，不难）
        ep_r += r
        # 假如我们总训练2000次，
        # 在训练第i_episode（200）次后，我们数据库中累计的信息超过3000条后。
        # 这个时 dqn中的数据库中的记忆条数  大于 数据库的容量
        if dqn.memory_counter > MEMORY_CAPACITY:
            # 它就会开对去学习。
            # eavl 每学一次就会更新一次  # 它的更新思路是从我历史记忆中随机抽取数据。 #学习一次，就在数据库中随机挑选BATCH_SIZE（32条） 进行打包

            # 而target不一样，它是在我们学习过程中到一定频率（TARGET_REPLACE_ITER，来决定）。它的思路是：target网会去复制eval网的参数
            dqn.learn()
            # 在满足 大于数据库容量的条件下，我再看env.step(a) 返回的done，env是否认为实验结束了
            if done:
                # 如果done=True , 打印这是第n次训练和这次训练的总分
                # 打印这是i_episode次训练 ， Ep_r代表这次的总分
                print('Ep: ', i_episode,
                      '| Ep_r: ', round(ep_r, 2))
        # if done=Truue
        # env判断游戏结束跳出while循环，开始进行下一次训练
        if done:
            break
        # env判断游戏没有结束进行while循环，下次状态变成当前状态， 开始走下一步。
        s = s_