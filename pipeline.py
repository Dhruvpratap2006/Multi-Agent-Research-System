# here we are going to connect all things
# so that all things get work in one sequence

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain, factcheck_chain
from langchain_core.messages import ToolMessage

def run_research_pipeline(topic : str) -> dict :

    state = {}
    # in this state we are going to store all the data of each step 
    # means search_agent will gave some output, reader agent , writer_chain and critic_agent
    # so for storing the oputput we are going to use the state dict 

    # search agent working
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    }) 

    # NAYA: ToolMessage se raw search results (jisme URLs hain) nikaalo
    from langchain_core.messages import ToolMessage
    
    tool_outputs = [
        msg.content for msg in search_result['messages'] 
        if isinstance(msg, ToolMessage)
    ]
    
    state['search_results'] = "\n\n".join(tool_outputs)

      #step 2 - reader agent 
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content
    print("\nscraped content: \n", state['scraped_content'])

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    # saving the report in state which is the output of the writer_chain
    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

# saving the feedback in state which is the output of the critic_chain
    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

        #fact-checker
    print("\n"+" ="*50)
    print("step 5 - fact-checker is verifying claims ...")
    print("="*50)

    state["factcheck"] = factcheck_chain.invoke({
        "research": research_combined,
        "report": state['report']
    })

    print("\n fact-check result \n", state['factcheck'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)

    
