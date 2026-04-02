import re
import copy
import json
import time
from simhash import Simhash

class LingoBP:
    NODE_DIC = {
        'cn': {
            'user': ['用户需求分析',  '有用性策略'],
            'developer':['用户需求分析', '风险意图分析', '安全准则响应', '安全策略','有用性策略' ],
             'strategy_name': '回复策略制定'},
        'en': {
            'user': ['User Needs Analysis', 'Usefulness Strategies'],
            'developer': ['User Needs Analysis', 'Risk Intent Analysis', 'Safety Guidelines', 'Safety Strategies', 'Usefulness Strategies' ],
            'strategy_name': 'Response Strategy Formulation'}
    }
    UPDATE_NODE_DIC = {
        'cn': {
            'user': ['User-更新后的用户需求分析',  'User-更新后的有用性策略集合'],
            'developer':['Developer-更新后的用户需求分析', 'Developer-更新后的风险意图分析', 'Developer-更新后的安全准则响应', 'Developer-更新后的安全策略集合', 'Developer-更新后的有用性策略集合'],
            'both': ['Developer-更新后的用户需求分析', 'Developer-更新后的风险意图分析', 'Developer-更新后的安全准则响应', 'Developer-更新后的安全策略集合', 'Developer-更新后的有用性策略集合']},
        'en': {
            'user': ['User-Updated User Needs Analysis', 'User-Updated Usefulness Strategies'],
            'developer': ['Developer-Updated User Needs Analysis', 'Developer-Updated Risk Intent Analysis', 'Developer-Updated Safety Guidelines', 'Developer-Updated Safety Strategies', 'Developer-Updated Usefulness Strategies' ],
            'both': ['Developer-Updated User Needs Analysis', 'Developer-Updated Risk Intent Analysis', 'Developer-Updated Safety Guidelines', 'Developer-Updated Safety Strategies', 'Developer-Updated Usefulness Strategies' ]}
    }
    def __init__(self, q):
        self.q = q
        with open("./prompts/update_prompts.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        self.prompts = {}
        for language, prompts_dict in data.items():
            self.prompts[language] = {}        
            for prompt_type, file_path in prompts_dict.items():
                with open(file_path, 'r', encoding='utf-8') as prompt_file:
                    prompt_content = prompt_file.read()          
                self.prompts[language][prompt_type] = prompt_content
    @staticmethod
    def minimal_strategies_update(S, S_prime, max_change_num=2):
        def simhash_similarity(str1, str2):
            hash1 = Simhash(str1).value
            hash2 = Simhash(str2).value
            hamming = bin(hash1 ^ hash2).count('1')
            return 1.0 - hamming / 64

        original_S = S
        if len(S_prime) < 3:
            return original_S
        if isinstance(S, str):
            S_processed = S.replace('；', ';')
            s_list = S_processed.split(';')
        elif isinstance(S, list):
            s_list = S.copy() if hasattr(S, 'copy') else list(S)
        else:
            raise TypeError("S must be a string or a list")

        if isinstance(S_prime, str):
            S_prime_processed = S_prime.replace('；', ';')
            s_prime_list = S_prime_processed.split(';')
        elif isinstance(S_prime, list):
            s_prime_list = S_prime.copy() if hasattr(S_prime, 'copy') else list(S_prime)
        else:
            raise TypeError("S_prime must be a string or a list")

        set_s = set(s_list)
        set_s_prime = set(s_prime_list)
        num_diff = len(set_s.symmetric_difference(set_s_prime))
        if num_diff <= max_change_num:
            return ';'.join(list(set_s))

        common = set_s & set_s_prime
        common_list = list(common)
        if not common:
            max_sim = -1
            selected_replace = None
            for s_prime in s_prime_list:
                current_max = max(
                    simhash_similarity(s_prime, s) for s in s_list
                )
                if current_max > max_sim:
                    max_sim = current_max
                    selected_replace = s_prime
            max_s = max(
                s_list,
                key=lambda x: simhash_similarity(x, selected_replace)
            )
            new_s_list = []
            for s in s_list:
                if s == max_s:
                    new_s_list.append(selected_replace)
                else:
                    new_s_list.append(s)
            candidates = [sp for sp in s_prime_list if sp != selected_replace]
            if not candidates:
                return ','.join(new_s_list)
            selected_add = None
            min_avg_sim = float('inf')
            for candidate in candidates:
                avg_sim = sum(
                    simhash_similarity(candidate, s) for s in s_list
                ) / len(s_list)
                if avg_sim < min_avg_sim:
                    min_avg_sim = avg_sim
                    selected_add = candidate
            new_s_list.append(selected_add)
            return ','.join(new_s_list)
        else:
            candidates = [sp for sp in s_prime_list if sp not in common]
            if not candidates:
                return ','.join(common_list)
            selected_add = None
            min_avg_sim = float('inf')
            for candidate in candidates:
                avg_sim = sum(
                    simhash_similarity(candidate, s) for s in s_list
                ) / len(s_list)
                if avg_sim < min_avg_sim:
                    min_avg_sim = avg_sim
                    selected_add = candidate
            new_s_list = common_list.copy()
            new_s_list.append(selected_add)
            return ';'.join(new_s_list)

    @staticmethod
    def get_structed_chain(text, language, authority="developer"):
        if isinstance(text, dict):
            return text
        elif isinstance(text, str):
            try:
                # 新增的完整try逻辑
                text = text.replace('user需求分析', '用户需求分析')
                text = text.replace('用户体验策略', '有用性策略')
                text = text.replace('Usefulness Strategies', 'Usefulness Strategies')
                json_blocks = re.findall(r"```json(.*?)```", text.replace('\n', ''), re.DOTALL)
                if not json_blocks:
                    raise ValueError("No JSON block found")
                    
                parsed_json = json.loads(json_blocks[-1])
                thinking_data = parsed_json.get('thinking', {})
                
                # 动态构建结果结构
                if language == "cn":
                    if authority == "user":
                        result = {
                            "用户需求分析": thinking_data.get("用户需求分析", ""),
                            "回复策略制定": {
                                "有用性策略": thinking_data.get("回复策略制定", {}).get("有用性策略", "").replace(',', ';').replace('，', ';').replace('；', ';'),
                            }
                        }
                    else:
                        result = {
                            "用户需求分析": thinking_data.get("用户需求分析", ""),
                            "风险意图分析": thinking_data.get("风险意图分析", ""),
                            "安全准则响应": thinking_data.get("安全准则响应", ""),
                            "回复策略制定": {
                                "有用性策略": thinking_data.get("回复策略制定", {}).get("有用性策略", "").replace(',', ';').replace('，', ';').replace('；', ';'),
                                "安全策略": thinking_data.get("回复策略制定", {}).get("安全策略", "").replace(',', ';').replace('，', ';').replace('；', ';')
                            }
                        }
                else:
                    if authority == "user":
                        result = {
                            "User Needs Analysis": thinking_data.get("User Needs Analysis", ""),
                            "Response Strategy Formulation": {
                                "Usefulness Strategies": thinking_data.get("Response Strategy Formulation", {}).get("Usefulness Strategies", "").replace(',', ';'),
                            }   
                        }
                    else:
                        result = {
                            "User Needs Analysis": thinking_data.get("User Needs Analysis", ""),
                            "Risk Intent Analysis": thinking_data.get("Risk Intent Analysis", ""),
                            "Safety Guidelines": thinking_data.get("Safety Guidelines", ""),
                            "Response Strategy Formulation": {
                                "Usefulness Strategies": thinking_data.get("Response Strategy Formulation", {}).get("Usefulness Strategies", "").replace(',', ';'),
                                "Safety Strategies": thinking_data.get("Response Strategy Formulation", {}).get("Safety Strategies", "").replace(',', ';')
                            }
                        }
                return result
                
            except:
                # 原有except逻辑保持不变
                if language == "cn":
                    if authority == "user":
                        result = {
                            "用户需求分析": "",
                            "回复策略制定": {"有用性策略": ""}  
                        }
                        patterns = {
                            "用户需求分析": r'"用户需求分析":\s*"((?:\\"|“|”|[^"])*)"',
                            "有用性策略": r'"有用性策略":\s*"([^"]*)"'
                        }
                    else:
                        result = {
                            "用户需求分析": "",
                            "风险意图分析": "",
                            "安全准则响应": "",
                            "回复策略制定": {"有用性策略": "","安全策略": ""}
                        }
                        patterns = {
                            "用户需求分析": r'"用户需求分析":\s*"((?:\\"|“|”|[^"])*)"',
                            "风险意图分析": r'"风险意图分析":\s*"((?:\\"|""|[^"])*)"',
                            "安全准则响应": r'"安全准则响应":\s*"([^"]*)"',
                            "安全策略": r'"安全策略":\s*"([^"]*)"',
                            "有用性策略": r'"有用性策略":\s*"([^"]*)"'
                        }
                else:
                    if authority == "user":
                        result = {
                            "User Needs Analysis": "",
                            "Response Strategy Formulation": {"Usefulness Strategies": ""},
                        }
                        patterns = {
                            "User Needs Analysis": r'"User Needs Analysis":\s*"((?:\\"|“|”|[^"])*)"',
                            "Usefulness Strategies": r'"Usefulness Strategies":\s*"([^"]*)"'
                        }
                    else:
                        result = {
                            "User Needs Analysis": "",
                            "Risk Intent Analysis": "",
                            "Safety Guidelines": "",
                            "Response Strategy Formulation": {"Usefulness Strategies": "","Safety Strategies": ""}
                        }
                        patterns = {
                            "User Needs Analysis": r'"User Needs Analysis":\s*"((?:\\"|“|”|[^"])*)"',
                            "Risk Intent Analysis": r'"Risk Intent Analysis":\s*"((?:\\"|“|”|[^"])*)"',
                            "Safety Guidelines": r'"Safety Guidelines":\s*"((?:\\"|""|[^"])*)"',
                            "Safety Strategies": r'"Safety Strategies":\s*"([^"]*)"',
                            "Usefulness Strategies": r'"Usefulness Strategies":\s*"([^"]*)"'
                        }
                
                for field, pattern in patterns.items():
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        content = match.group(1).replace('""', '"').replace('“', '"').replace('”', '"')
                        
                        if field in ["安全策略", "有用性策略"]:
                            result["回复策略制定"][field] = content.replace(',', ';')
                        elif field in ["Safety Strategies", "Usefulness Strategies"]:
                            result["Response Strategy Formulation"][field] = content.replace(',', ';')
                        else:
                            result[field] = content
                            
                return result

    def call_api(self, prompt, chain):
        retry, success = 0, False
        new_chain = copy.deepcopy(chain)
        while retry < 3 and not success:
            retry += 1
            try:
                _, output = self.q.talk('', prompt)
                a = re.findall("```json(.*?)```", output.replace('\n', ''), re.S)
                result = json.loads(a[-1])
                success = True
            except Exception as e:
                print("API failed, retry3, 错误原因: %s" % e)
                time.sleep(2)
        return success, result

    ## 根据调用更新结果
    def update_chain_with_bp(self, hierarchy_bp, chain, result, language, authority="developer"):
        structured_chain = self.get_structed_chain(chain, language, authority="developer")
        if authority == 'user':
            structured_chain[hierarchy_bp[authority][0]] = result[self.UPDATE_NODE_DIC[language][authority][0]] 
            print(structured_chain[hierarchy_bp[authority][0]])
            print(result[self.UPDATE_NODE_DIC[language][authority][0]]  )
            structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp[authority][1]] = self.minimal_strategies_update(result[self.UPDATE_NODE_DIC[language][authority][1]] , structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp[authority][1]])
        elif (authority == 'developer') or (authority == 'both'):
            structured_chain[hierarchy_bp[authority][0]] = result[self.UPDATE_NODE_DIC[language][authority][0]] 
            structured_chain[hierarchy_bp[authority][1]] = result[self.UPDATE_NODE_DIC[language][authority][1]] 
            structured_chain[hierarchy_bp[authority][2]] = result[self.UPDATE_NODE_DIC[language][authority][2]] 
            structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp[authority][3]] = self.minimal_strategies_update(result[self.UPDATE_NODE_DIC[language][authority][3]], structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp[authority][3]])
            structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp[authority][4]] = self.minimal_strategies_update(result[self.UPDATE_NODE_DIC[language][authority][4]], structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp[authority][4]])
        else:
            raise ValueError("authority must be 'user', 'developer' or 'both'")
        return structured_chain
    def bp_and_update(self, query, chain, response, user_judge, safe_judge, language, bp_type='both'):
        hierarchy_bp = {
            "user": self.NODE_DIC[language]['user'],
            "developer": self.NODE_DIC[language]['developer']
        }
        structured_chain = self.get_structed_chain(chain, language, authority=bp_type)

        if bp_type == 'user':
            user_strategy_collection = structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp['user'][1]]
            user_needs = structured_chain[hierarchy_bp['user'][0]]
            prompt = self.prompts[language]['user_update']
            prompt = prompt.replace('{query}', query).replace('{response}', response).replace('{user_judge}', str(user_judge)).replace('{user_strategy_collection}', user_strategy_collection).replace('{user_needs}', user_needs)
            success, result = self.call_api(prompt, chain)
            if not success:
                raise RuntimeError("API call failed for user BP type")
            else:
                new_chain = self.update_chain_with_bp(hierarchy_bp, chain, result, language, authority='user')
        elif bp_type == 'developer':
            user_needs = structured_chain[hierarchy_bp['developer'][0]]
            risk_intent = structured_chain[hierarchy_bp['developer'][1]]
            safety_guidelines = structured_chain[hierarchy_bp['developer'][2]]
            develeper_strategy_collection = structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp['developer'][3]]
            user_strategy_collection = structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp['developer'][4]]
            prompt = self.prompts[language]['developer_update']
            prompt = prompt.replace('{query}', query).replace('{response}', response).replace('{safe_judge}', str(safe_judge)).replace('{user_strategy_collection}', user_strategy_collection).replace('{develeper_strategy_collection}', develeper_strategy_collection).replace('{needs}', user_needs).replace('{risk_intent}', risk_intent).replace('{safety_guidelines}', safety_guidelines)
            success, result = self.call_api(prompt, chain)
            if not success:
                raise RuntimeError("API call failed for user BP type")
            else:
                new_chain = self.update_chain_with_bp(hierarchy_bp, chain, result, language, authority='developer')
        elif  bp_type == 'both':

            user_needs = structured_chain[hierarchy_bp['developer'][0]]
            risk_intent = structured_chain[hierarchy_bp['developer'][1]]
            safety_guidelines = structured_chain[hierarchy_bp['developer'][2]]
            develeper_strategy_collection = structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp['developer'][3]]
            user_strategy_collection = structured_chain[self.NODE_DIC[language]['strategy_name']][hierarchy_bp['developer'][4]] 
            prompt = self.prompts[language]['both_update']
            prompt = prompt.replace('{query}', query).replace('{response}', response).replace('{user_judge}', str(user_judge)).replace('{safe_judge}', str(safe_judge)).replace('{user_strategy_collection}', user_strategy_collection).replace('{develeper_strategy_collection}', develeper_strategy_collection).replace('{needs}', user_needs).replace('{risk_intent}', risk_intent).replace('{safety_guidelines}', safety_guidelines)
            success, result = self.call_api(prompt, chain)
            if not success:
                raise RuntimeError("API call failed for BP type 'both'")
            else:
                new_chain = self.update_chain_with_bp(hierarchy_bp, chain, result,language, authority='developer')
        else:
            raise ValueError("bp_type must be 'user', 'developer' or 'both'")
     
        return new_chain