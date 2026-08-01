import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("严重错误：找不到 API Key！")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

# 咱们的本地工具函数
def get_system_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[本地系统] 🤖 咔哒！工具被真实触发，读取到本地时间: {current_time}")
    return current_time

def run_agent():
    print(">>> 引擎点火完毕，带有工具的 Agent 开始运行...\n")
    
    # 将对话记录做成一个列表，方便后续追加记录
    messages = [
        {"role": "system", "content": "你是一个极简、干脆的硬核 AI 助手。遇到不知道的信息，必须果断使用工具。"},
        {"role": "user", "content": "我现在本地电脑上的准确时间是几点几分？"}
    ]
    
    try:
        # 第一次通信：向云端发送问题和工具说明书
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=[{
                "type": "function",
                "function": {
                    "name": "get_system_time",
                    "description": "当用户询问当前时间、今天几号等问题时，调用此工具获取本地系统的准确时间。"
                }
            }],
            tool_choice="required",
            temperature=0
        )
        
        message = response.choices[0].message
        # 关键步骤：把大模型的工具调用请求也存入历史记录中
        messages.append(message) 
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            print("\n====== Agent 思考过程 ======")
            print(f"大模型没有瞎编，它请求调用本地工具: {tool_call.function.name}")
            
            # 1. 真实执行本地函数
            if tool_call.function.name == "get_system_time":
                tool_result = get_system_time()
                
                # 2. 把函数的运行结果打包，追加到历史记录里
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
                
                print("====== 正在将真实数据传回云端大脑 ======\n")
                
                # 3. 第二次通信：让大模型根据真实时间生成最终的人类语言回答
                second_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages
                )
                
                print(f"🌟 大模型最终回复: {second_response.choices[0].message.content}")
                
    except Exception as e:
        print(f"\n运行报错: {e}")

if __name__ == "__main__":
    run_agent()