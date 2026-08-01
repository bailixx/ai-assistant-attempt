import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# 第一步：唤醒保险箱，加载密钥
# 这行代码会在后台默默打开你刚才建的 .env 文件，把密钥读进系统内存
load_dotenv()

# 从内存中提取具体的 API 钥匙
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("严重错误：找不到 API Key，请检查 .env 文件是否配置正确！")

# 第二步：初始化通信客户端 (引擎核心)
# 默认这是连接 OpenAI 的标准写法。
# 如果你买的是 DeepSeek 等其他兼容接口，只需要取消下面 base_url 的注释并填入正确的地址
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1" 
)

# 咱们的本地工具函数
def get_system_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[本地系统] 🤖 咔哒！工具被真实触发，读取到本地时间: {current_time}")
    return current_time

# 新增点 1：写一个纯本地的 Python 函数（工具）
def get_system_time():
    """获取本地机器的当前准确时间"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[本地系统运行中...] 工具被触发，获取到本地时间: {current_time}")
    return current_time

# 第三步：封装 Agent 的首次通信逻辑
def run_first_test():
    print(">>> 引擎点火完毕，正在向云端大模型发送请求...\n")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # 如果用其他模型，比如 deepseek，请改成 "deepseek-chat"
            messages=[
                {"role": "system", "content": "你是一个极简、干脆的硬核 AI 助手。"},

                {"role": "user", "content": "用一句话向我证明，你已经成功连接到了我的本地开发环境。"}
            ],
            # 新增点 2：把工具的“说明书”递给大模型
            tools=[{
                "type": "function",
                "function": {
                    "name": "get_system_time",
                    "description": "当用户询问当前时间、今天几号等问题时，调用此工具获取本地系统的准确时间。"
                }
            }],
            tool_choice="required",# <--- 就是新增这一行！剥夺它的自主决定权，强制它必须用工具
            temperature=0.7 # 控制回答的随机性，0 最严谨，1 最发散
        )
        
        message = response.choices[0].message

        if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
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
        print(f"连接失败，报错信息: {e}")

if __name__ == "__main__":
    run_first_test()