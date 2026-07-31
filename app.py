#==========Load Module===========
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from tavily import TavilyClient
import pytesseract as pyt
import numpy as np
import streamlit as st

#============API Keys============
GOOGLE_API_KEY=st.sidebar.text_input("Google-API",type="password")
GROQ_API_KEY=st.sidebar.text_input("Groq-API",type="password")
TAVILY_API_KEY=st.sidebar.text_input("Tavily-API",type="password")

os.environ["GOOGLE_API_KEY"]=GOOGLE_API_KEY
os.environ["GROQ_API_KEY"]=GROQ_API_KEY
os.environ["TAVILY_API_KEY"]=TAVILY_API_KEY


ALL_API=[GOOGLE_API_KEY,GROQ_API_KEY,TAVILY_API_KEY]

if not all(ALL_API):
  st.sidebar.error("PASS API-KEYS")
elif all(ALL_API):
  st.sidebar.info("MUST PASS ALL API KEYS")
elif all(ALL_API):
  # Step 1:Model Call
  model=ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GOOGLE_API_KEY
)
  st.sidebar.success("API KEYS LOADED SUCCESSFULLY")
elif any(ALL_API):
  st.sidebar.ifo("MUST PASS ALL API KEYS")
else:
  st.info("LOADED")
   
#===============FRONTEND===============
st.title("AI-AGENT-POWERED BY PPT GENERATOR")
user_query=st.text_area("write your ppt topic or prompt")
#===============ASSESTs=================
#tool 1
def search_latest_info(query):
  """This function search latest
  news or content from website
  using tavily, helpful to check
  trending content"""
  client = TavilyClient (api_key = TAVILY_API_KEY)
  response = client.search(query)
  return response

#tool 2
def generate_image(img_prompt):
  """This function,helps to generate Image
  using free api,with given
  img_prompt using pollinations"""

  url = f"https://image.pollinations.ai/{img_prompt}"
  #file handling
  import requests as r
  content=r.get(url).content
  with open(f"Image.jpeg",'wb')as f:
    f.write(content)
    
  from PIL import Image
  return url

#WITH TABS
tab1,tab2,tab3=st.tabs(["GENERATE IMAGE",
                       "CHECK LATEST NEWS",
                      "GENERATE PPT"
                       ])
#detailed prompt
def prompt_generator(model,query):
  prompt=f"""your task is to give detailed prompt instructions
  for given.
  prompt:
  You are a Professional PPT generator,where
  user will give the query and based on that,
  you have to generate dynamic,HTML output based
  ppt with advanced CSS and Dynamic UI and UX with
  PPT toggle button,Based on Query take image reference to generate
  and embed the same in ppt,using
  Image ref: url = https://images.unsplash.com/photo, 
  or url = https://image.pollinations.ai/, 
  make sure img src must be valid, and image must be
  present inside html, Generate
  pollinations:url=https://image.pollinations.ai/img_prompt,Generate
  with image caption, and no markdowns
  user query given below:{query}
  """
  response=model.invoke(prompt)
  final_prompt=response.content[-1]['text']

  with open("ppt_prompt.txt",'w') as f:
    f.write(final_prompt)
  return final_prompt
if all(ALL_API)and user_query:

  agent=create_agent(
      model=model,
      tools=[search_latest_info,
             generate_image
  ]
  )
  #===========DISPLAY AGENT============
  #st.sidebar.Image(agent)
  #=========WITH TABS=========
  with tab1:
    st.header("GENERATE IMAGE GIVE PROMPT")
    if st.button("Click to Generate:",key="generate_image_button"):
      with st.spinner("Running Agent.."):
        data =  f"https://image.pollinations.ai/{user_query}"
        time.sleep(3)
        st.image(data)
        st.image("Image.jpeg")
  with tab2:
    st.header("CHECK LATEST NEWS")
    if st.button("Fetch news: ",key="news_button"):
      with st.spinner ("Running Agent.."):
  
        prompt = """Give latest news India or word wind related
        to tech, business, jobs, or user requested Output
        In Proper HTML News Templates""" + user_query
        
        response = agent.invoke({'messages': [{'role': "user",
                                          "content":prompt}]})
        code=response['messages'][-1].content[-1]['text']
        
        st.html(code,width="stretch",
                unsafe_allow_javascript=True)
  
  with tab3:
    st.header("Create PPT")
    if st.button("Click to generate: ",key="generate_ppt_button"):
      with st.spinner ("Running Agent.."):
        final_prompt = prompt_generator (model, user_query)
        
        response = agent.invoke({'messages': [{'role':"user",
                                               "content":final_prompt}]})
        
        code = response['messages'] [-1].content[-1]['text']
        st.html(code, width="stretch",
                unsafe_allow_javascript=True)
        if st.download_button(label = "DOWNLOAD PPT",
                           data=code,
                           file_name = 'ppt.html',
                           mime = 'text/html'):
          st.success("PPT Downloaded Successfully!!")
    
