import time
def reorder_dict(original_dict,  current_layer=None):
    """
    按照指定顺序重排字典的特定层级。
    
    :param original_dict: 原始字典
    :param layer_keys_order: 分层键顺序，例如 {'thinking': ['用户需求分析', '风险意图分析', ...]}
    :param current_layer: 当前处理的层级键
    :return: 排序后的字典
    """
    if current_layer is None:
        current_layer = original_dict
    layer_keys_order = { 'thinking': ['用户需求分析', '风险意图分析', '安全准则响应', '回复策略制定']
}
    for key, order in layer_keys_order.items():
        if key in current_layer and isinstance(current_layer[key], dict):
            ordered_subdict = {k: current_layer[key][k] for k in order if k in current_layer[key]}
            current_layer[key] = ordered_subdict

    return original_dict

def combine_chain(q,query,chain, language):

    general_flag = False
    if language == "cn":
        with open("./prompts/cn/structured_chain_recombine.txt", "r", encoding="utf-8") as f:
            system = f.read()
        system = system.replace("{{chain}}", str(chain))
        if ("无风险" in chain['风险意图分析'] ) or (chain['风险意图分析'] == "") or (chain['安全准则响应'] == ""):
            general_flag = True
            new_chain = {
                "用户需求分析": chain['用户需求分析'],
                "回复策略制定":  chain['回复策略制定']['有用性策略'] + ";" + chain['回复策略制定']['安全策略']
                }
            system = system.replace("{{chain}}", str(new_chain))
    else:
        with open("./prompts/en/structured_chain_recombine.txt", "r", encoding="utf-8") as f:
            system = f.read()
        system = system.replace("{{chain}}", str(chain))
        if ("No risk" in chain['Risk Intent Analysis'] ) or (chain['Risk Intent Analysis'] == "") or (chain['Safety Guidelines'] == ""):
            general_flag = True
            new_chain = {
                "User Needs Analysis": chain['User Needs Analysis'],
                "Response Strategy Formulation":  chain['Response Strategy Formulation']['Usefulness Strategies'] + ";" + chain['Response Strategy Formulation']['Safety Strategies']
                }
            system = system.replace("{{chain}}", str(new_chain))
            
    prompt = query
    retry,success = 0,False
    while retry<3 and not success:
        retry += 1
        try: 
            think,output = q.talk(system,prompt)
            success= True
        except Exception as e:
            print("API failed, retry4, 错误原因: %s" % e)
            time.sleep(3)
    if success:
        if general_flag:
            return new_chain, think, output
        else:
            return chain, think,output
    else:
        return None
