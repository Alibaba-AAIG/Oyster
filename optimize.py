from typing import Generator, Union
import time
import random
import re
import os
import json
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser
import copy
from simhash import Simhash
from datetime import datetime
import textwrap
import sys
import threading
import queue
from utils.QwQ import QWQ
from players.user import *
from players.developer import *
from lingo_bp import LingoBP
from utils.utils import *
def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--platform', type=str, required=True, choices=['sampool', 'whale'])
    parser.add_argument('--iterations', type = list, required=False, default=['both','both', 'both'], help="iterations for optimization, e.g. ['user','developer'] or ['both','both']")
    parser.add_argument("--input", type=str, required=True, help="input xlsx/csv path, with col trace_id,sys_prompt,user_prompt")
    parser.add_argument("--output_dir", type=str, required=True, help="output dir")
    parser.add_argument("--token", type=str, required=True, help="your sampool token")
    parser.add_argument("--opt_pruning", type=bool, required=False, default=False, help="whether to prune during the optimization, default True")   
    parser.add_argument("--opt_summarize", type=bool, required=False, default=False, help="whether to summarize the optimization, default False")   
    parser.add_argument("--batch_size", type=int, required=False,default= 100, help="your sampool token")
    parser.add_argument("--start_idx", type=int, required=False, default = 0, help="start idx")
    parser.add_argument("--interval", type=int, required=False, default = 2000, help="data idx interval")
    parser.add_argument("--sys_prompt_path", type=str, required=False, default= "", help="system prompt path") 
    parser.add_argument("--model", type=str, required=False, default="qwen-qwq-plus", help="qwen-qwq-plus/qwen-qwq-32b/deepseek-r1")
    args = parser.parse_args()
    return args
args = parse_args()
def print_args(args):
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script_name = sys.argv[0].split('/')[-1]
    
    args_dict = {
        "INPUT PATH": args.input,
        "TOKEN": f"{args.token[:4]}****{args.token[-4:]}" if len(args.token) > 8 else "****",
        "START INDEX": args.start_idx,
        "SYS PROMPT": args.sys_prompt_path if args.sys_prompt_path else "N/A",
        "MODEL": args.model
    }
    
    header = f"🚀 Launching {script_name}"
    print(f"\n{'═' * 60}")
    print(f"{header:^{60}}")
    print(f"{'Timestamp: ' + time_str:^{60}}")
    print(f"{'═' * 60}")
    
    max_key_length = max(len(str(k)) for k in args_dict.keys())
    for key, value in args_dict.items():
        print(f"│ {key.ljust(max_key_length)} │ {str(value).ljust(40 - max_key_length)} │")
    
    print(f"{'═' * 60}")
    print(textwrap.dedent(f"""
    📝 Command line reproduction:
      $ python {script_name} \\
        --input "{args.input}" \\
        --token "{args.token}" \\
        --start_idx {args.start_idx} \\
        {"--sys_prompt_path " + args.sys_prompt_path if args.sys_prompt_path else ""} \\
        --model {args.model}
    """))
    print(f"{'═' * 60}\n")
    
print_args(args)

args.model = "QwQ-32B" if args.platform == "whale" else args.model

q = QWQ(
    platform=args.platform,
    token=args.token,
    model_type=args.model
)

def get_judge_results(query, response, risk_type, risk_intention, side):
    u = Userv3(q)
    d = Developer_zq(q)
    if side == 'user':
        user_judge = u.user_preference_judge(query, response)
        return user_judge, 'None'
    elif side == 'developer':
        safe_judge = d.developer_preference_judge(query, response, risk_type)
        return 'None',safe_judge
    elif side == 'both':
        user_judge = u.user_preference_judge(query, response)
        safe_judge = d.developer_preference_judge(query, response, risk_type)
        return user_judge,safe_judge
    else:
        print('side must be user/developer/both')


def get_judge_score(user_info, developer_info):
    try:
        user_judge = user_info["user_judge"]
    except:
        user_judge = user_info
    try:
        safe_judge = developer_info["safe_judge"]
    except:
        safe_judge = developer_info
    return user_judge, safe_judge
        
def optimize_chain(risk_type, risk_intention, query, chain, think, response, language, iterations = ['both','both']):
    lingobp = LingoBP(q)
    ###  INI 
    user_info, developer_info = get_judge_results(query, response, risk_type,risk_intention, iterations[0])
    user_judge, safe_judge = get_judge_score(user_info, developer_info)
    history = [ {
                'query': query,
                "chain":chain,
                "think":think,
                "response":response,
                "user_judge":copy.deepcopy(user_info),
                "safe_judge":copy.deepcopy(developer_info),}] 
    print("%%%%%%%%%%%%%%%%%%%%Initial query%%%%%%%%%%%%%%%%%%%%")
    print("query: ", query[:100])
    print("chain: ", chain)
    print("think: ", think)
    print("response: ", response)
    ###  Iter 0 -> N   
    for i in tqdm(range(len(iterations))):
        print("%%%%%%%%%%%%%%%%%%%% Iteration %d %%%%%%%%%%%%%%%%" % i)
        if (i !=  0) and args.opt_pruning:
            if (iterations[i] == 'both') and (safe_judge['score'] == 1) and( user_judge['score'] == 1):
                break
            elif iterations[i] == 'user' and user_judge['score'] == 1:
                break
            elif iterations[i] == 'developer' and safe_judge['score'] == 1:
                break
        new_chain = lingobp.bp_and_update(query,chain, response, user_judge, safe_judge, language, iterations[i])
        general_chain, new_think,new_response = combine_chain(q,query,new_chain, language)
        chain = copy.deepcopy(new_chain)
        think = copy.deepcopy(new_think)
        response = copy.deepcopy(new_response)
        user_info, developer_info = get_judge_results(query, response, risk_type,risk_intention,iterations[i])
        user_judge, safe_judge = get_judge_score(user_info, developer_info)
        print("%%%%%%%%%%%%%%%%%%%%优化后%%%%%%%%%%%%%%%%%%%%")
        print("query: ", query[:100])
        print("chain: ", chain)
        print("think: ", think)
        print("response: ", response)
        print("general_chain: ", general_chain if general_chain!=new_chain else "" )
        print("user_judge: ", user_judge)
        print("safe_judge: ", safe_judge)
        history.append({
                          'query': query,
                          "chain":chain,
                          "general_chain": general_chain if general_chain!=new_chain else "",
                          "think":think,
                          "response":response,
                          "user_judge":copy.deepcopy(user_info),
                          "safe_judge":copy.deepcopy(developer_info)})
    return history


class Task:
    """封装单个数据处理任务"""
    def __init__(self, idx, data_row):
        language = data_row["Language"]
        risk_type,risk_intention,query,chain,think,response,language = data_row["Risk_type"], data_row["Risk_intent"], data_row["Query"], data_row["Safety_chain"], data_row["Initial_think"], data_row["Initial_response"], data_row["Language"]
        self.idx = idx
        self.language = language
        self.risk_type = risk_type
        self.risk_intention = risk_intention
        self.query = query
        self.chain = chain
        self.think = think
        self.response = response
        self.max_retries = 10
        self.retries = 0



class Scheduler(threading.Thread):
    def __init__(self, task_queue ,input_data, iterations):
        super().__init__()
        self.task_queue = task_queue
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.last_call_time = 0
        self.last_log_time = time.time()
        self.running = True 
        self.time_step = 0.5
        self.log_step = 300
        self.pool_size = 100
        self.doing_num = 0
        self.done_num = 0
        self.all_num = len(input_data)
        self.results = []
        self.input_data = input_data
        self.iterations = iterations
    def input_tasks(self):
        for idx, datarow in self.input_data.iterrows():
            task = Task(idx, datarow)
            self.task_queue.put(task)
        return
    
    def run(self):
        while self.running:
            with self.lock:
                if time.time()-self.last_log_time>self.log_step:
                    passed_time = time.time()-self.start_time
                    remain_time = (passed_time/(self.done_num+1))*(self.all_num-self.done_num)
                    print(f"runing:{self.doing_num},done:{self.done_num},all:{self.all_num},passed:{passed_time:.1f}s,remaining:{remain_time:.1f}s")
                    self.last_log_time = time.time()
                if not self.task_queue.empty() and self.doing_num<self.pool_size:
                    # 计算需要等待的时间
                    current_time = time.time()
                    elapsed = current_time - self.last_call_time
                    if elapsed < self.time_step:
                        wait_time = self.time_step - elapsed
                        time.sleep(wait_time)
                    
                    task = self.task_queue.get()
                    threading.Thread(
                        target=self.process_task,
                        args=(task,),
                        daemon=True
                    ).start()
                    
                    self.last_call_time = time.time()
                    self.doing_num += 1
                    #print(f"发送任务 {task.trace_id} at {time.time()-self.start_time:.1f}s")
                else:
                    if self.done_num==self.all_num:
                        passed_time = time.time()-self.start_time
                        self.running = False
                    else:
                        time.sleep(1)

    def process_task(self, task):
        while task.retries <= task.max_retries:
            try:
                history = optimize_chain(task.risk_type, task.risk_intention, task.query, task.chain, task.think, task.response, task.language, self.iterations)

                self.results.append(
                    {"id": task.idx,
                    "input_data": args.input,
                    "original_QTR":{
                            "query": task.query,
                            "think": task.think,
                            "response": task.response
                        },
                    "optimize_history": history}
                )

                self.done_num += 1
                self.doing_num -=1
                break
            except Exception as e:
                task.retries += 1
                if task.retries > task.max_retries:
                    print(f"任务{task.idx}失败，达到最大重试次数{task.max_retries}")
                    history = "FAIL"
                    self.results.append(
                        {"id": task.idx,
                        "input_data_source": args.input,
                        "original_QTR":{
                                "query": task.query,
                                "think": task.think,
                                "response": task.response
                            },
                        "optimize_history": history}
                    )
                    self.done_num += 1
                    self.doing_num -=1
                    break
                print(f"任务{task.idx}发生异常{e}，正在重试第{task.retries}次...")
                time.sleep(5)

        self.task_queue.task_done()
    def get_output(self):
        passed_time = time.time()-self.start_time
        print(f"tasks all done!! total time cost:{passed_time:.1f}s")
        print("writing to output file")

        return self.results

def get_batch_output_data( input_data, iterations=['both','both']):
    task_queue = queue.Queue()
    scheduler = Scheduler(task_queue, input_data, iterations)
    scheduler.daemon = True
    scheduler.start()
    scheduler.input_tasks()
    task_queue.join()
    optimize_history = scheduler.get_output()
    return optimize_history


if __name__ == "__main__":

    if '.csv' in args.input:
        df = pd.read_csv(args.input)
    elif '.xlsx' in args.input:
        df = pd.read_excel(args.input)
    elif '.json' in args.input:
        df = pd.read_json(args.input)
    else:
        raise ValueError("only support .xlsx or .csv input file")
    df = df.replace({float('nan'): ''})
    df = df.reset_index(drop=True)
    df = df[args.start_idx:]
    df = df[200:210]
    print("总共数据量:", len(df))


    output_file_name = args.input.replace('.json', '_opt.json').split("/")[-1]
    output_path = os.path.join(args.output_dir, output_file_name)
    
    #######For debugging
    optimize_history = []
    for idx, datarow in tqdm(df.iterrows(), total=len(df)):
        risk_type,risk_intention,query,chain,think,response,language = datarow["Risk_type"], datarow["Risk_intent"], datarow["Query"], datarow["Safety_chain"], datarow["Initial_think"], datarow["Initial_response"], datarow["Language"]
        history = optimize_chain(risk_type, risk_intention, query, chain, think, response, language, iterations = args.iterations)
        optimize_history.append(
                        {"id": idx,
                        "input_data_source": args.input,
                        "original_QTR":{
                            "query": datarow['Query'],
                            "think": datarow['Initial_think'],
                            "response": datarow['Initial_response']
                        },
                        "optimize_history": history}
                    )
        json.dump(optimize_history,open(output_path,'w'),ensure_ascii=False,indent=2)
    json.dump(optimize_history,open(output_path,'w'),ensure_ascii=False,indent=2)
    exit()

    # if args.opt_summarize:
    #     iter_score
    #     for data_item in optimize_history:
            



    optimize_history = []
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            cur_optimize_history = json.load(f)
        for item in cur_optimize_history:
            try:
                if item["optimize_history"] == "FAIL":
                    continue
                else:
                    optimize_history.append(item)
            except:
                continue
        print("当前已经优化的数据数量:", len(optimize_history))
        args.start_idx = len(optimize_history)
    for idx in range(len(optimize_history), len(df), args.batch_size):
        if idx + args.batch_size > len(df):
            df_batch = df[idx:len(df)] 
        else:
            df_batch = df[idx:idx + args.batch_size] 
        output_data = get_batch_output_data( df_batch, args.iterations)
        optimize_history.extend(output_data)
        json.dump(optimize_history,open(output_path,'w'),ensure_ascii=False,indent=2)

    json.dump(optimize_history,open(output_path,'w'),ensure_ascii=False,indent=2)

