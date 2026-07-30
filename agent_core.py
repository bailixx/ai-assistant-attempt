import os
import json
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
    base_url="https://api.deepseek.com/v1"  # 如果用第三方大模型，把这行最前面的 # 删掉
)

# 第三步：封装 Agent 的首次通信逻辑
def run_first_test():
    print(">>> 引擎点火完毕，正在向云端大模型发送请求...\n")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # 如果用其他模型，比如 deepseek，请改成 "deepseek-chat"
            messages=[
                # System 是给大模型的“人设”和“系统级指令”
                {"role": "system", "content": "你是一个极简、干脆的硬核 AI 助手。"},
                # User 是你作为用户发出的指令
                {"role": "user", "content": "用一句话向我证明，你已经成功连接到了我的本地开发环境。"}
            ],
            temperature=0.7 # 控制回答的随机性，0 最严谨，1 最发散
        )
        
        # 提取并打印最核心的回答文本
        reply = response.choices[0].message.content
        print("====== 收到大模型回传信号 ======")
        print(reply)
        print("=================================")
        
    except Exception as e:
        print(f"连接失败，报错信息: {e}")

# Python 工程标准起手式
if __name__ == "__main__":
    run_first_test()