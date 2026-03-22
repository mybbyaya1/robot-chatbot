from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts,load_system_prompts


@wrap_tool_call
def monitor_tool(
        #请求的数据封装
        request:ToolCallRequest,
        #工具调用的函数
        handler:Callable[[ToolCallRequest],ToolMessage | Command],
)->ToolMessage | Command:
    logger.info(f"[monitor_tool工具调用]开始:执行工具：{request.tool_call['name']}")
    logger.info(f"[monitor_tool工具调用]开始:传入参数：{request.tool_call['args']}")
    try:
        res=handler(request)
        logger.info(f"[monitor_tool工具调用]成功:返回结果：{res}")
        if request.tool_call['name']=="fill_context_for_report":
            request.runtime.context['report']=True
        return res
    except Exception as e:
        logger.error(f"[monitor_tool工具调用]异常:{str(e)}")
        raise e

@before_model
def log_before_model(
        state:AgentState,
        runtime:Runtime,
):
    logger.info(f"[log_before_model]开始执行任务：带有{len(state['messages'])}条消息。")
    logger.info(f"[log_before_model]开始{type(state['messages'][-1]).__name__},消息内容：{state['messages'][-1].content.strip()}")
    return None





@dynamic_prompt
def report_prompt_switch(request:ModelRequest):#动态切换提示词
    isreport= request.runtime.context.get('report',False)
    if isreport:
        return load_report_prompts()
    return load_system_prompts()