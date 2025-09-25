# 🐳 PeppinoxAI – Docker Assistant

**PeppinoxAI** is an intelligent assistant powered by **Large Language Model (LLM)** that helps manage and orchestrate Docker containers using natural language.  
Users can simply write commands ihn natural language to create, run, stop, or remove containers without remembering the `docker` command syntax.  

---

## ✨ Key Features
- Automatically create a Flask (or Nginx) app inside a Docker container with a custom message.  
- Enrich the app with HTML content (headings, buttons, banners, etc.).  
- Build custom Docker images or official ones (e.g., Nginx).  
- Start, stop, and remove existing containers.  
- Clean up unnecessary Docker images.  
- Interactive interface: just type natural language commands, and PeppinoxAI takes care of the rest.  

---

## 🚀 How It Works
1. The user writes a command, e.g., *“Create a Flask app with the message ‘Welcome’ on port 8080”*.  
2. PeppinoxAI translates the request into a sequence of Docker actions (file creation → image build → container run).  
3. The assistant returns the operation status and the local URL to visit.  

---

## 🧩 Architecture
- **LLM**: currently powered by Google Gemini-flash (via `langchain` and `langchain_google_genai`).  
- **Docker Tools**: a collection of Python functions executing Docker commands through `subprocess`.  
- **LangChain Agent**: coordinates the model and the tools, guided by a custom system prompt.  

---

## 📌 Project Status
This is the **first version** of PeppinoxAI (v0.1).  
The project is experimental and may receive updates and improvements in the future, such as:  
- Adding graphical interfaces.  
- Extending to Kubernetes or Podman.  
- Supporting more application templates beyond Flask.
