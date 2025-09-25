import os
import subprocess
from langchain.agents import Tool, AgentType, initialize_agent 
from langchain.chat_models import init_chat_model 
from langchain_google_genai import ChatGoogleGenerativeAI 

#=====================================================================================================#
# LLM CONFIG
#=====================================================================================================#

os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"
llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai", temperature = 0)

#=====================================================================================================#
# DOCKER TOOLS
#=====================================================================================================#

def list_containers(_):
    result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
    return result.stdout

def run_container(cmd: str):
    """Start a container with complete shell command (docker run -d -p ...).
       If the container is a Flask one, <host_port>:5000
    """
    if cmd.startswith("cmd="):
        cmd = cmd.replace("cmd=", "").strip(" '\"")

    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    if result.returncode != 0:
        return f"Errore run: {result.stderr}"
    return result.stdout if result.stdout else result.stderr

def build_flask_image(image_name: str):
    """Build Docker image for Flask app."""
    result = subprocess.run(["docker", "build", "-t", image_name, "."], capture_output=True, text=True)
    return result.stdout if result.stdout else result.stderr

def build_nginx(_=None):
    """Download official Nginx image from Nginx website."""
    result = subprocess.run(["docker", "pull", "nginx:latest"], capture_output=True, text=True)
    return result.stdout if result.stdout else result.stderr

def stop_container(container_name: str):
    result = subprocess.run(["docker", "stop", container_name], capture_output=True, text=True)
    return result.stdout if result.stdout else result.stderr

def remove_container(container_name: str):
    result = subprocess.run(["docker", "rm", container_name], capture_output=True, text=True)
    return result.stdout if result.stdout else result.stderr

def create_flask_app(message: str = "Hello, World! From Flask container", port: int = 5000):
    """Create base files for a Flask app with Dockerfile."""
    app_code = f'''from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return """{message}"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port={port})
'''

    requirements = "flask==2.3.2\n"

    dockerfile = '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
'''

    with open("app.py", "w") as f:
        f.write(app_code)
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)

    return "File Flask created: app.py, requirements.txt, Dockerfile."

def remove_image(image_name: str):
    """Remove Docker images knowing name or ID."""
    try:
        result = subprocess.run(["docker", "rmi", image_name], capture_output=True, text=True, check=True)
        return f"Image '{image_name}' succesfully removed."
    except subprocess.CalledProcessError as e:
        return f"Error removing image: {e.stderr.strip()}"

#=====================================================================================================#
# TOOLS REGISTRATION
#=====================================================================================================#

docker_tools = [
    Tool(name="CreateFlaskApp", func=create_flask_app,
        description="Create Flask app files. Input: 'message, port', Output: 'message'."),

    Tool(name="BuildFlaskImage", func=build_flask_image,
        description="Build Docker images for Flask app (my-flask-app)."),

    Tool(name="BuildNginx", func=build_nginx,
        description="Download official Nginx image."),

    Tool(name="RunContainer", func=run_container,
        description="Run Docker container. Input = complete command shell (docker run ...). If container is a Flask one, <host_port>:5000"),

    Tool(name="ListContainers", func=list_containers,
        description="Show activated and deactivated containers."),

    Tool(name="StopContainer", func=stop_container,
        description="Stop a container knowing its name or ID."),

    Tool(name="RemoveContainer", func=remove_container,
        description="Remove a container knowing its name or ID."),

    Tool(name="RemoveImage", func=remove_image,
         description="Remove Docker images knowing its name or ID. Use this tools to remove images that you don't need anymore.")
]

#=====================================================================================================#
# AGENT
#=====================================================================================================#

system_prompt = (
    "You are PeppinoxAI, a Docker expert assistant.\n"
    "\n"
    "--- INSTRUCTIONS ---\n"
    "1. To create a **Flask app**:\n"
    "   a. Use CreateFlaskApp → generate the files (input: 'message, port').\n"
    "   b. Use BuildFlaskImage → build the image with the name 'my-flask-app'.\n"
    "   c. Use RunContainer → start with:\n"
    "      docker run -d -p <host_port>:5000 --name my-flask-container my-flask-app\n"
    "   Final response: confirm success and show URL http://localhost:<host_port>\n"
    "\n"
    "2. To create an **Nginx container**:\n"
    "   a. Use BuildNginx → pull the official image.\n"
    "   b. Use RunContainer → start with:\n"
    "      docker run -d -p <host_port>:80 --name my-nginx-container nginx:latest\n"
    "   Final response: confirm success and show URL http://localhost:<host_port>\n"
    "\n"
    "3. Use ListContainers, StopContainer, RemoveContainer for management.\n"
    "4. Feel free to talk freely about other topics if requested.\n"
    "5. With RemoveImage → remove one or more Docker images from the image list. "

)

agent = initialize_agent(
    tools=docker_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={"system_message": system_prompt}
)

#=====================================================================================================#
# WHILE CYCLE
#=====================================================================================================#

print("\n=== PeppinoxAI - Docker Assistant ===")
print("Write commands in natural language ('exit' or 'quit' to close this app).\n")

while True:
    user_input = input("Prompt > ")
    print("=======================================")
    if user_input.lower() in ["exit", "quit"]:
        break
    try:
        output = agent.invoke({"input": user_input})["output"]
        print("\n[Output]:\n", output)
    except Exception as e:
        print("[Error]:", e)
