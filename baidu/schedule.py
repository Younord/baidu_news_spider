# coding = utf-8
import time
import os
import sched
import datetime

schedule = sched.scheduler(time.time, time.sleep)


def perform_command(cmd, inc):
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    os.system(cmd)


def timming_exe(cmd, inc=60):
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    schedule.run()


os.system('python3 -m scrapy crawl baiduNews')
print("show time after 1 days:")
timming_exe('python3 -m scrapy crawl baiduNews', 86400)
print(datetime.timedelta(days=1).total_seconds())

#
# import sched
# import time
# import os
# # 初始化sched模块的scheduler类
# # 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
# schedule = sched.scheduler(time.time, time.sleep)
#
# # 被周期性调度触发的函数
# def func():
#     os.system("python3 -m scrapy crawl baiduNews")
#
# def perform1(inc):
#     schedule.enter(inc, 0, perform1, (inc,))
#     func()    # 需要周期执行的函数
#
# def mymain():
#     schedule.enter(0, 0, perform1, (86400,))
#
# if __name__=="__main__":
#     mymain()
#     schedule.run()  # 开始运行，直到计划时间队列变成空为止

# import datetime
# import os
#
# def run_Task():
#     # os.system("dir")
#     print('run_Task')
#
# def timerFun(sched_Timer):
#     flag = 0
#     while True:
#         now_time = datetime.datetime.now()
#         if now_time == sched_Timer:
#             print('hello')
#             run_Task()
#             flag = 1
#         else:
#             print('no')
#             if flag == 1:
#                 sched_Timer = sched_Timer + datetime.timedelta(seconds=5)
#                 flag = 0
#
# if __name__ == '__main__':
#     sched_Timer = datetime.datetime(2017, 6, 13, 14, 39, 10)
#     print(sched_Timer)
#     print('run the timer task at {0}'.format(sched_Timer))
#     timerFun(sched_Timer)
