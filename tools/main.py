from typing import List, Dict, Any

from fastapi import  HTTPException
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool # Use tool decorator for simplicity
from utils.common import get_redis_message_history
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from tools.seat_profile import get_seat_profile_tool
from tools.rag import ask_rag_question
from config import OPENAI_API_KEY


# --- Environment Setup ---
openai_api_key = OPENAI_API_KEY
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# --- Tool Registry ---
# Collect all defined tools
tools = [get_seat_profile_tool, ask_rag_question]
tool_map = {t.name: t for t in tools} # Dictionary to easily access tools by name

# --- LLM Setup ---
# Use gpt-4o-mini - good balance of capability and cost/speed
# Temperature 0 for more predictable tool usage
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)

# Bind tools to the LLM. This tells the LLM which tools are available.
llm_with_tools = llm.bind_tools(tools)


# --- Request/Response Models ---


class AnswerResponse(BaseModel):
    answer: str = Field(..., description="The final answer from the LLM.")
    tool_calls_made: List[Dict[str, Any]] = Field(default_factory=list, description="Details of any tools called during processing.")

# --- API Endpoint ---
async def ask_llm_with_tools(question: str, session_id: str, headers: Dict[str, str]):
    """
    Receives a question, processes it using the LLM, potentially calls tools,
    and returns the final answer.
    Based on the tool output, the LLM will call the tool again.
    """
    print("headers",headers)
    print(f"--- Session ID: {session_id} ---")
    # Generate or reuse session_id
    chat_history = get_redis_message_history(session_id)
    # Reconstruct messages from Redis
    messages = chat_history.messages.copy()
    # Add the current user question
    prompt_instruction = (
    "You are a helpful assistant processing a user's request within an ongoing conversation. "
    "Please answer the user's latest question based *first* on the information available in our "
    "conversation history (including previous tool calls and their results). "
    "Only use the available tools if the answer cannot be found or requires updated information "
    "not present in the history.\n\n"
    "User's current question: "
)

    user_message = HumanMessage(content=f"{prompt_instruction} {question}")
    messages.append(user_message)
    chat_history.add_message(user_message)
   
    tool_calls_made_info = []
    try:
        # 2. First LLM call - Let the LLM decide if it needs a tool
        ai_msg: AIMessage = llm_with_tools.invoke(messages)
        messages.append(ai_msg) # Add the AI's response (which might include tool calls)

        print(f"--- Initial LLM Response: {ai_msg} ---")

        # 3. Check for Tool Calls and Execute them
        if ai_msg.tool_calls:
            print(f"--- LLM requested tool calls: {ai_msg.tool_calls} ---")
            tool_messages = [] # Store results from tool calls

            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_call_id = tool_call.get("id") # Important for matching response

                print(f"  - Tool: {tool_name}, Args: {tool_args}, ID: {tool_call_id}")

                if tool_name in tool_map:
                    selected_tool = tool_map[tool_name]
                    try:
                        # Execute the tool
                        print(f"  - Executing tool: {tool_name}")
                        tool_args["headers"] = headers
                        tool_output = await selected_tool.ainvoke(tool_args)
                        print(f"  - Tool Output: {tool_output}")
                        # Record the call for the response
                        tool_calls_made_info.append({
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "output": tool_output # Be careful about exposing sensitive output
                        })
                        # Create a ToolMessage with the output
                        tool_messages.append(
                            ToolMessage(content=str(tool_output), tool_call_id=tool_call_id)
                        )
                    except Exception as e:
                        print(f"  - Error executing tool {tool_name}: {e}")
                        # Inform the LLM the tool failed
                        tool_messages.append(
                             ToolMessage(content=f"Error executing tool {tool_name}: {str(e)}", tool_call_id=tool_call_id)
                        )
                        tool_calls_made_info.append({
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "error": str(e)
                        })
                else:
                    print(f"  - Error: Tool '{tool_name}' not found.")
                    # Inform the LLM the tool doesn't exist
                    tool_messages.append(
                        ToolMessage(content=f"Error: Tool '{tool_name}' not found.", tool_call_id=tool_call_id)
                    )
                    tool_calls_made_info.append({
                            "tool_name": tool_name,
                            "arguments": tool_args,
                            "error": "Tool not found"
                        })

            # 4. Second LLM Call (if tools were called) - Provide tool results back to LLM
            if tool_messages:
                messages.extend(tool_messages) # Add tool results to history
                print(f"--- Calling LLM again with tool results ---")
                final_response: AIMessage = llm_with_tools.invoke(messages) # Use llm_with_tools again in case it needs *another* tool
                print(f"--- Final LLM Response after tool calls: {final_response.content} ---")
                messages.append(final_response)
                chat_history.add_message(final_response)
                answer = final_response.content
            else:
                 # Should not happen if ai_msg.tool_calls was non-empty, but as fallback:
                 answer = ai_msg.content # Use the initial response if tool execution somehow failed entirely

        else:
            # 5. No Tool Calls Needed - The first response is the final answer
            print("--- No tool calls requested by LLM ---")
            answer = ai_msg.content

        return AnswerResponse(answer=answer, tool_calls_made=tool_calls_made_info)

    except Exception as e:
        print(f"Error processing request: {e}")
        # Log the exception traceback here in a real app
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
