# we are nopt going to use the react agent as they are older version 
# so we are going to use the create_agent librabry in the langchain

from dotenv import load_dotenv
load_dotenv()

import os
import requests

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 


llm = ChatMistralAI(model="open-mistral-nemo", temperature=0)

# 1st agent => search agent
def build_search_agent() :
    return create_agent( # using create_agent
        model=llm,
        tools=[web_search]
    )

#2nd agent = reader agent
def build_reader_agent() :
    return create_agent(
        model=llm,
        tools=[scrape_url   ]
    )


# now we are going to make a chains(runables)

# 1st chain => writer_chain
# this will take the all scrap content and make a well structured, well-written research report
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

    Topic: {topic}

    Research Gathered:
    {research}

    Structure the report as:
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (list all URLs found in the research)

    Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic chain
# now the report which is created by writer_chain now this will going to be checked 
# by the critic chain that report is accurate or not and gave a feedback and score 
# like the senior interviewer
critic_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a sharp and constructive research critic. Be honest and specific."),
        ("human", """Review the research report below and evaluate it strictly.

        Report:
        {report}

        Respond in this exact format:

        Score: X/10

        Strengths:
        - ...
        - ...

        Areas to Improve:
        - ...
        - ...

        One line verdict:
        ..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()


# fact-checker chain
# this will compare the writer's report against the original scraped content
# to catch any hallucinated/unsupported claims
factcheck_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a meticulous fact-checker. Your job is to verify claims against source material, not to judge writing quality."),
    ("human", """Compare the research report below against the original source content it was based on.

    Original Source Content:
    {research}

    Report to Verify:
    {report}

    For each major claim in the report, check if it is actually supported by the source content.

    Respond in this exact format:

    Verified Claims:
    - ...

    Unsupported/Questionable Claims:
    - ...

    Overall Accuracy: X/10

    One line verdict:
    ..."""),
])

factcheck_chain = factcheck_prompt | llm | StrOutputParser()