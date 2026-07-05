````markdown
# 🚀 OrbitLearn

**OrbitLearn** is an AI-powered educational assistant built using **Google Agent Development Kit (ADK)**. It helps students learn topics through interactive conversations while demonstrating modern agent engineering concepts from Google's AI Agents course.

## 🌟 Features

- 📚 Interactive educational AI assistant
- 🤖 Built with Google ADK
- 🔌 MCP (Model Context Protocol) server integration
- ⚡ FastAPI backend
- 🧠 ReAct-style reasoning workflow
- 🔒 Secure project structure with environment-based configuration
- 🧪 Evaluation and testing framework
- 🚀 Ready for deployment

---

## 🛠️ Technology Stack

- Python 3.12+
- Google Agent Development Kit (ADK)
- Google Agents CLI
- FastAPI
- MCP (Model Context Protocol)
- Uvicorn
- UV Package Manager
- Git & GitHub

---

## 📁 Project Structure

```
orbitlearn/
├── app/
│   ├── agent.py
│   ├── config.py
│   ├── fast_api_app.py
│   ├── mcp_server.py
│   └── app_utils/
├── deployment/
├── tests/
├── Dockerfile
├── pyproject.toml
├── agents-cli-manifest.yaml
├── README.md
└── uv.lock
```

---

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/soorajraju5/OrbitLearn.git
cd OrbitLearn
```

### Install dependencies

```bash
uv sync
```

### Configure environment

Create a `.env` file and add the required API keys and configuration.

### Run the application

```bash
uv run adk web
```

or

```bash
uv run python -m app.fast_api_app
```

---

## 🧪 Evaluation

The project includes evaluation and testing support.

Run tests:

```bash
pytest
```

---

## 📚 Course Concepts Demonstrated

This project demonstrates multiple concepts from Google's AI Agents course, including:

- ✅ Google Agent Development Kit (ADK)
- ✅ MCP (Model Context Protocol) Server
- ✅ Antigravity IDE development workflow
- ✅ FastAPI agent deployment
- ✅ Evaluation framework
- ✅ Secure configuration using environment variables

---

## 🎯 Use Case

OrbitLearn aims to make learning more engaging by providing an AI-powered educational assistant capable of answering questions, guiding students through concepts, and demonstrating modern agent engineering techniques.

---

## 📦 Deployment

The project includes deployment-ready configuration using:

- Docker
- FastAPI
- Terraform configuration
- Google Cloud deployment templates

---

## 👨‍💻 Author

**Sooraj Raju**

GitHub: https://github.com/soorajraju5

---

## 📄 License

This project was developed as part of the **Kaggle AI Agents: Intensive Vibe Coding Capstone Project**.
````
