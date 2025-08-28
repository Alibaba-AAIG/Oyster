import pandas as pd
from sampool import SampoolDashScopeInvoker, SampoolDashScopeChatRequest, SampoolDashScopeResponse
from typing import Generator, Union
import time
import json
import threading
import queue
import random
import sys
import os
import re
from utils.QwQ import QWQ
from argparse import ArgumentParser
import textwrap
from datetime import datetime
def parse_args():
    parser = ArgumentParser()
    # 必需参数
    parser.add_argument("--input", type=str, required=True, 
                      help="input file name")
    parser.add_argument("--token", type=str, required=True,
                      help="Sampool 访问令牌")
    parser.add_argument('--platform', type=str, required=True, choices=['sampool', 'whale'])
    
    # 多阶段控制
    stage_group = parser.add_argument_group('Pipeline Stages')
    stage_group.add_argument("--stage_inference", action='store_true',
                           help="是否执行推理阶段")
    stage_group.add_argument("--stage_risk_analysis", action='store_true',
                           help="是否执行风险分析阶段")
    stage_group.add_argument("--stage_safety_chain_extract", action='store_true',
                           help="是否执行安全链抽取阶段")
    stage_group.add_argument("--stage_safety_chain_recombine", action='store_true',
                           help="是否执行安全链重组阶段")

    # 可选参数
    parser.add_argument("--language", type=str, default="cn", choices=["en", "cn"],
                      help="query language (cn/en)")
    parser.add_argument("--model", type=str, default="qwen-qwq-plus",
                      choices=["qwen-qwq-plus", "qwen-qwq-32b", "gpt4o-mini"],
                      help="Sampool model type")
    parser.add_argument("--start_idx", type=int, default=0,
                      help="数据起始索引 (支持断点续跑)")
    parser.add_argument("--end_idx", type=int, default=0,
                      help="数据结束索引 (支持断点续跑)")
    parser.add_argument("--max_cnt", type=int, default=0,
                      help="最大数据数")
    return parser.parse_args()

args = parse_args()
def print_args(args):
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    script_name = sys.argv[0].split('/')[-1]
    
    masked_token = (f"{args.token[:4]}****{args.token[-4:]}" 
                    if len(args.token) > 8 else "****")

    args_config = {
        "INPUT PATH": args.input,
        "TOKEN": masked_token,
        "LANGUAGE": args.language.upper(),
        "START INDEX": args.start_idx,
        "MODEL": args.model
    }
    
    stage_status = {
        "INFERENCE": "✅" if args.stage_inference else "❌",
        "RISK ANALYSIS": "✅" if args.stage_risk_analysis else "❌",
        "SAFETY EXTRACT": "✅" if args.stage_safety_chain_extract else "❌",
        "SAFETY RECOMBINE": "✅" if args.stage_safety_chain_recombine else "❌"
    }

    header = f"🚀 Launching {script_name}"
    separator = '═' * 60
    
    print(f"\n{separator}")
    print(f"{header:^{60}}")
    print(f"{'Timestamp: ' + time_str:^{60}}")
    print(separator)
    
    max_key_length = max(len(k) for k in args_config.keys())
    for key, value in args_config.items():
        print(f"│ {key.ljust(max_key_length)} │ {str(value).ljust(40 - max_key_length)} │")
    
    print(separator.replace('═', '─'))
    print("│ Pipeline Stages Status:")
    for stage, status in stage_status.items():
        print(f"│   {status} {stage.ljust(22)}")
    
    print(separator)
    cmd_args = [
        f'python {script_name}',
        f'--input "{args.input}"',
        f'--token "{args.token}"',
        f'--language {args.language}',
        f'--start_idx {args.start_idx}',
        f'--model {args.model}'
    ]
    for stage in ["inference", "risk_analysis", "safety_chain_extract", "safety_chain_recombine"]:
        if getattr(args, f"stage_{stage}"):
            cmd_args.append(f'--stage_{stage}')
    
    print("📝 Command line reproduction:")
    print("  $ " + " \\\n    ".join(cmd_args))
    print(separator + "\n")
    
print_args(args)


class Llm:
    def __init__(self,args):
        self.q=q = QWQ(
    platform=args.platform,
    token=args.token,
    model_type=args.model
    )

    def query(self, inputs):
        return self.q.talk(*inputs)

class Task:
    def __init__(self, trace_id, inputs):
        self.trace_id = trace_id
        self.inputs = inputs
        self.max_retries = 5
        self.retries = 0

class Scheduler(threading.Thread):
    def __init__(self, task_queue, llm ,input_data):
        super().__init__()
        self.task_queue = task_queue
        self.llm = llm
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.last_call_time = 0
        self.last_log_time = time.time()
        self.running = True 
        self.time_step = 1.2
        self.log_step = 300
        self.pool_size = 30
        self.doing_num = 0
        self.done_num = 0
        self.all_num = len(input_data)
        self.results = {}
        self.input_data = input_data
    def input_tasks(self):
        for line in self.input_data:
            task = Task(line[0],[line[1],line[2]])
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
                        time.sleep(0.1)

    def process_task(self, task):
        while task.retries <= task.max_retries:
            try:
                result = self.llm.query(task.inputs)
                self.results[task.trace_id] = result
                self.done_num += 1
                self.doing_num -=1
                break
            except Exception as e:
                task.retries += 1
                if task.retries > task.max_retries:
                    print(f"任务{task.trace_id}失败，达到最大重试次数{task.max_retries}")
                    result = (None,None)
                    self.results[task.trace_id] = result
                    self.done_num += 1
                    self.doing_num -=1
                    break
                print(f"任务{task.trace_id}发生异常{e}，正在重试第{task.retries}次...")
                time.sleep(3)

        self.task_queue.task_done()

    def get_output(self):
        passed_time = time.time()-self.start_time
        print(f"tasks all done!! total time cost:{passed_time:.1f}s")
        print("writing to output file")
        output_data = []
        for line in self.input_data:
            trace_id = line[0]
            output_data.append(line+[self.results[trace_id][0],self.results[trace_id][1]])
        return output_data

def white_check_and_rewrite(think, language):
    think = think.replace('user需求分析', '用户需求分析')
    json_blocks = re.findall(r"```json(.*?)```", think.replace('\n', ''), re.DOTALL)
    if not json_blocks:
        raise ValueError("No JSON block found")
    parsed_json = json.loads(json_blocks[-1])
    think = parsed_json.get('thinking', {})
    if language == "cn":
        if ("无风险" in think['风险意图分析'] ) or (think['风险意图分析'] == "") or (think['安全准则响应'] == ""):
            new_think = {
                "用户需求分析": think['用户需求分析'],
                "回复策略制定":  think['回复策略制定']['有用性策略'] + ";" + think['回复策略制定']['安全策略']
                }
            return new_think
    else:
        if ("No risk" in think['Risk Intent Analysis'] ) or (think['Risk Intent Analysis'] == "") or (think['Safety Guidelines'] == ""):
            new_think = {
                "User Needs Analysis": think['User Needs Analysis'],
                "Response Strategy Formulation":  think['Response Strategy Formulation']['Usefulness Strategies'] + ";" + think['Response Strategy Formulation']['Safety Strategies']
                }
            print(new_think)
            return new_think
    
    return think
    
def get_batch_output_data(args, input_data):
    llm = Llm(args)
    task_queue = queue.Queue()
    scheduler = Scheduler(task_queue, llm, input_data)
    scheduler.daemon = True
    scheduler.start()
    scheduler.input_tasks()
    task_queue.join()
    output_data = scheduler.get_output()
    return output_data


output_file_name = args.input
output_path = os.path.join(args.output_dir, output_file_name)

if os.path.exists(output_path):
    args.input = output_path
if '.csv' in args.input:
    df = pd.read_csv(args.input)
elif '.xlsx' in args.input:
    df = pd.read_excel(args.input)
elif '.json' in args.input:
    df = pd.read_json(args.input)
else:
    raise ValueError("only support .xlsx or .csv input file")
df = df.replace({float('nan'): ''})

if args.max_cnt != 0:
    df = df[:args.max_cnt]


if args.end_idx == 0: 
    df = df[args.start_idx:]
else:
    df = df[args.start_idx:  args.end_idx]
    
prompts_dir = os.path.join("./prompts", args.language)
with open(os.path.join(prompts_dir,  'risk_analysis.txt'),'r') as file:
    risk_analysis_sys_prompt = file.read()
with open(os.path.join(prompts_dir, 'safety_chain_extract.txt'), 'r') as file:
    safety_chain_extract_sys_prompt = file.read()
with open(os.path.join(prompts_dir, 'structure_chain_recombine.txt'), 'r') as file:
    safety_chain_recombine_sys_prompt = file.read()


input_data = {}
if args.stage_inference:
    input_data["inference_stage"] = []
if args.stage_safety_chain_extract:
    input_data["safety_chain_extract_stage"] =  []
if args.stage_safety_chain_recombine:
    input_data["safety_chain_recombine_stage"] =  []

batch_size = 20

for idx in df.index.to_list():

    df.loc[idx, "Language"] = args.language
    if args.stage_inference:

        input_data['inference_stage'].append([idx, "", df.loc[idx]["Query"]])
        if len(input_data['inference_stage']) == batch_size:
            output_data = get_batch_output_data(args, input_data['inference_stage'])
            index = [row[0] for row in output_data]
            df_o = pd.DataFrame(output_data, columns=['trace_id','sys_prompt', 'user_prompt','think','response'],index=index)
            for trace_id in df_o.index.to_list():
                df.loc[trace_id, "Initial_think"] = df_o.loc[trace_id]["think"]
                df.loc[trace_id, "Initial_response"] = df_o.loc[trace_id]["response"]
            input_data['inference_stage'] = []
            df.to_json(output_path, orient='records', force_ascii=False)

            print("*************************{}/{}**************************".format(idx, len(df)))

if args.stage_inference and (len(input_data['inference_stage'])!=0):
    output_data = get_batch_output_data(args, input_data['inference_stage'])
    index = [row[0] for row in output_data]
    df_o = pd.DataFrame(output_data, columns=['trace_id','sys_prompt', 'user_prompt','think','response'],index=index)
    for trace_id in df_o.index.to_list():
        df.loc[trace_id, "Initial_think"] = df_o.loc[trace_id]["think"]
        df.loc[trace_id, "Initial_response"] = df_o.loc[trace_id]["response"]
    input_data['inference_stage'] = []
    df.to_json(output_path, orient='records', force_ascii=False)

    print("*************************{}/{}**************************".format(idx, len(df)))

for idx in df.index.to_list():
    if args.stage_safety_chain_extract:
        if len(set(df["Initial_think"])) <= 2:
            print("该数据尚未完成前置初始化 ！！！")
            exit()
        input_data['safety_chain_extract_stage'].append([idx, safety_chain_extract_sys_prompt, df.loc[idx]["Initial_think"]])        
        if len(input_data['safety_chain_extract_stage']) == batch_size:
            output_data = get_batch_output_data(args, input_data['safety_chain_extract_stage'])
            index = [row[0] for row in output_data]
            df_o = pd.DataFrame(output_data, columns=['trace_id','sys_prompt', 'user_prompt','think','response'],index=index)
            for trace_id in df_o.index.to_list(): 
                pattern = r'```json\s*(.*?)\s*```' 
                try:
                    safety_chain_matches = re.findall(pattern, df_o.loc[trace_id]["response"], re.DOTALL) 
                    safety_chain_dict = json.loads(safety_chain_matches[0])
                    safety_chain = safety_chain_dict["safety_chain"]
                except:
                    safety_chain =  df_o.loc[trace_id]["response"]
                df.loc[trace_id, "Safety_chain"] = safety_chain
            input_data['safety_chain_extract_stage'] = []
            df.to_json(output_path, orient='records', force_ascii=False)
            print("*************************{}/{}**************************".format(idx, len(df)))
  
if args.stage_safety_chain_extract and (len(input_data['safety_chain_extract_stage'])!=0):
    output_data = get_batch_output_data(args, input_data['safety_chain_extract_stage'])
    index = [row[0] for row in output_data]
    df_o = pd.DataFrame(output_data, columns=['trace_id','sys_prompt', 'user_prompt','think','response'],index=index)
    for trace_id in df_o.index.to_list(): 
        pattern = r'```json\s*(.*?)\s*```' 
        try:
            safety_chain_matches = re.findall(pattern, df_o.loc[trace_id]["response"], re.DOTALL) 
            safety_chain_dict = json.loads(safety_chain_matches[0])
            safety_chain = safety_chain_dict["safety_chain"]
        except:
            safety_chain =  df_o.loc[trace_id]["response"]
        df.loc[trace_id, "Safety_chain"] = safety_chain
    input_data['safety_chain_extract_stage'] = []
    df.to_json(output_path, orient='records', force_ascii=False)

    print("*************************{}/{}**************************".format(idx, len(df)))    

for idx in df.index.to_list():
    if args.stage_safety_chain_recombine:
        if len(set(df["Initial_think"])) <= 2:
            print("该数据尚未完成前置初始化 ！！！")
            exit()

        thinking = df.loc[idx]["Initial_think"]
        try :
            thinking = white_check_and_rewrite(thinking, df.loc[idx]["Language"])
        except:
            pass
        safety_chain_recombine_sys_prompt = safety_chain_recombine_sys_prompt.replace('{{chain}}',thinking )
        input_data['safety_chain_recombine_stage'].append([idx, safety_chain_recombine_sys_prompt, df.loc[idx]["Query"]])
        if len(input_data['safety_chain_recombine_stage']) == batch_size:
            output_data = get_batch_output_data(args, input_data['safety_chain_recombine_stage'])
            index = [row[0] for row in output_data]
            df_o = pd.DataFrame(output_data, columns=['trace_id','sys_prompt', 'user_prompt','think','response'],index=index)
            for trace_id in df_o.index.to_list():
                df.loc[trace_id, "Safety_chain_recombine_think"] = df_o.loc[trace_id]["think"]
                df.loc[trace_id, "Safety_chain_recombine_response"] = df_o.loc[trace_id]["response"]
            input_data['safety_chain_recombine_stage'] = []
            df.to_json(output_path, orient='records', force_ascii=False)

            print("*************************{}/{}**************************".format(idx, len(df)))
if args.stage_safety_chain_recombine:
    if len(input_data['safety_chain_recombine_stage'])!=0:
        output_data = get_batch_output_data(args, input_data['safety_chain_recombine_stage'])
        index = [row[0] for row in output_data]
        df_o = pd.DataFrame(output_data, columns=['trace_id','sys_prompt', 'user_prompt','think','response'],index=index)
        for trace_id in df_o.index.to_list():
            df.loc[trace_id, "Safety_chain_recombine_think"] = df_o.loc[trace_id]["think"]
            df.loc[trace_id, "Safety_chain_recombine_response"] = df_o.loc[trace_id]["response"]
        df.to_json(output_path, orient='records', force_ascii=False)

        print("*************************{}/{}**************************".format(idx, len(df)))
            

df.to_json(output_path, orient='records', force_ascii=False)
