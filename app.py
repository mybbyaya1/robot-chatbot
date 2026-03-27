import time

import streamlit as st
from agent.react_agent import ReactAgent
st.title("mysql数据库学习机器人智能客服(微信：马jacket)")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"]=ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"]=[]

for message in st.session_state["message"]:
        st.chat_message("role").write(message["content"])

prompt=st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})
    ai_res_list=[]
    with st.spinner("智能客服机器人思考中..."):
        time.sleep(1)
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator,cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk
        st.chat_message("assistant").write_stream(capture(res_stream,ai_res_list))
        st.session_state["message"].append({"role": "assistant", "content":ai_res_list[-1] })