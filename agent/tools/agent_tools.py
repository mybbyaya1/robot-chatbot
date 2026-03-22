import os

from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random

from utils.config_handler import agent_conf
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

rag=RagSummarizeService()
#列10个ID,从1001开始，放在列表中，直接用数字的字符串，不要用循环
usder_ids=["1001","1002","1003","1004","1005","1006","1007","1008","1009","1010",]
#定义2025年1月到12月,格式为："2025-01","2025-02",不要用循环，直接列在列表中
month_arr=["2025-01","2025-02","2025-03","2025-04","2025-05","2025-06","2025-07","2025-08","2025-09","2025-10","2025-11","2025-12"]
external_data={}

@tool(description="从向量存储中检索参考资料")
def rag_summarize(query:str)->str:
    return rag.rag_summarize(query)

@tool(description="获取指定城市的天气，以消息字符串的形式返回")
def get_weather(city:str)->str:
    return f"{city}的天气是晴天，气温22度，风向北风。"

@tool(description="获取用户所在城市的名称，以纯字符串的形式返回")
def get_user_location()->str:
    return random.choice(["北京","上海","广州","深圳"])

@tool(description="获取用户的ID，以消息字符串的形式返回")
def get_user_id()->str:
    return f"用户ID是{random.choice(usder_ids)}"

@tool(description="获取指定月份的日历，以消息字符串的形式返回")
def get_current_month()->str:
    return "2025-03" #random.choice(month_arr)

def generate_external_data():
    '''
    {
       "user_id":
       {
          "month":{"特征":"xxx","时间":"xxx",...}
          "month":{"特征":"xxx","时间":"xxx",...}
          "month":{"特征":"xxx","时间":"xxx",...}
       }
    }
    :return:
    '''
    if not external_data:
        external_data_path=get_abs_path(agent_conf["external_data_path"])
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"{external_data_path}不存在")
        with open(external_data_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                arr:list[str]=line.strip().split(",")

                user_id:str=arr[0].replace('"',"")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id]={}

                external_data[user_id][time]={
                    "特征":feature,
                    "效率":efficiency,
                    "耗材":consumables,
                    "对比":comparison,
                }

@tool(description="从外部系统中获取用户在指定月份的使用记录，以消息字符串的形式返回，如未找到，返回空字符串")
def fetch_external_data(user_id:str,month:str)->str:
    generate_external_data()
    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"未找到用户{user_id}在{month}的使用记录")
        return ""

@tool(description="无入参，调用后触发中间件自动为报告生成的场景自动注入上下文信息，为后续的动态切换提示词提供信息")
def fill_context_for_report():
    return "fill_context_for_report"

if __name__ == '__main__':
    print(fetch_external_data("1001","2025-03"))




