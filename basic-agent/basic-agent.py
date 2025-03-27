import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool, BingGroundingTool, ToolSet
from azure.identity import DefaultAzureCredential
from pathlib import Path

def initialize_tools():
     # Create bing grounding tool
     bing_connection = project_client.connections.get(
         connection_name=os.getenv("BING_CONNECTION_NAME")
     )
     conn_id = bing_connection.id
     bing = BingGroundingTool(connection_id=conn_id)
    
     # Create code interpreter tool
     code_interpreter = CodeInterpreterTool()
    
     # Create toolset of tools
     toolset = ToolSet()
     toolset.add(bing)
     toolset.add(code_interpreter)
     return toolset

load_dotenv()
deployed_model = os.getenv("MODEL_DEPLOYMENT")
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True), conn_str=os.getenv("PROJECT_CONNECTION")
)

with project_client:
    # Get the toolset
    toolset = initialize_tools()

    # Create an agent
     # Create an agent
    agent = project_client.agents.create_agent(
        model=deployed_model,
        name="my-agent",
        instructions="You are a helpful agent who provides information about movie trends. Keep answers concise, but include as much relevant data as possible.",
        toolset=toolset,
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="What were the 10 most popular movies in 2024? Chart out the total gross revenue for those movies",
    )
    print(f"Created message, message ID: {message.id}")
        

    # Run the agent
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    # Get messages from the thread
    messages = project_client.agents.list_messages(thread_id=thread.id)
    
    # Uncomment to see the raw messages JSON
    print(f"Messages: {messages}")

    # Get the last message from the sender
    last_msg = messages.get_last_text_message_by_role("assistant")
    if last_msg:
        print(f"Last agent message: {last_msg.text.value}")

    # Generate an image file for the chart
    for image_content in messages.image_contents:
        print(f"Image File ID: {image_content.image_file.file_id}")
        file_name = f"{image_content.image_file.file_id}_image_file.png"
        project_client.agents.save_file(file_id=image_content.image_file.file_id, file_name=file_name)
        print(f"Saved image file to: {Path.cwd() / file_name}")

    # Delete the agent once done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
