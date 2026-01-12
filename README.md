# VidSage


<p align="center">
  <img src="doc/assets/image.png" alt="VidSage Logo" width="300"/>
</p>

<p align="center">
  <b>AI-powered Video Insights Platform</b><br/>
  <i>Unlock knowledge from videos with advanced search, summarization, and more.</i>
</p>


## 🚀 Overview


**VidSage** is a full-stack, production-grade application designed to extract, analyze, and interact with video content using state-of-the-art AI. Built as a portfolio project, VidSage demonstrates expertise in modern web development, scalable backend architecture, and seamless AI integration.


<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=FFD62E" alt="Vite"/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS"/>
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Jest-C21325?style=for-the-badge&logo=jest&logoColor=white" alt="Jest"/>
  <img src="https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white" alt="OpenAPI"/>
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js"/>
  <img src="https://img.shields.io/badge/Clerk-3A3A3A?style=for-the-badge&logo=clerk&logoColor=white" alt="Clerk"/>
  <img src="https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyBmaWxsPSIjRkZGIiB2aWV3Qm94PSIwIDAgMzAgMzAiIHdpZHRoPSIzMCIgaGVpZ2h0PSIzMCI+PHJlY3Qgd2lkdGg9IjMwIiBoZWlnaHQ9IjMwIiByeD0iNSIgZmlsbD0iIzAwMCIvPjx0ZXh0IHg9IjE1IiB5PSIyMCIgZm9udC1zaXplPSIxMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iI0ZGRiI+TEw8L3RleHQ+PC9zdmc+" alt="LangChain"/>
  <img src="https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini"/>
  <img src="https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white" alt="Azure"/>
</p>


## ✨ Features


### 🌟 What You Can Do with VidSage

- **Instant YouTube Video Summaries**: Paste any YouTube link and get a concise, AI-powered summary of the video content in seconds.
- **Listen to Summaries**: Prefer audio? Instantly listen to the generated video summaries for hands-free insights.
- **Ask Anything About a Video**: Chat with your videos! Ask questions and get smart, context-aware answers based on the video’s content.
- **Multi-Video Q&A**: Select multiple videos and ask questions that span across all their content for deep research and comparison.
- **Integrate with Your Favorite Tools**: Connect Google Drive and Notion to save summaries, research, and transcripts directly to your productivity apps.
- **Save & Revisit Your History**: All your processed videos and Q&A sessions are saved in your personal research library for easy access anytime.
- **Modern, Intuitive UI**: Enjoy a sleek, responsive interface designed for productivity and ease of use.


---

## 🖼️ Screenshots

<table align="center">
  <tr>
    <td align="center">
      <img src="doc/screenshots/home_dashboard.png" alt="Home Dashboard" width="400"/>
      <br/><b>Home Dashboard</b>
    </td>
    <td align="center">
      <img src="doc/screenshots/integrations_tools.png" alt="AI Integrations & Tools" width="400"/>
      <br/><b>AI Integrations & Tools</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="doc/screenshots/research_library.png" alt="Research Library" width="400"/>
      <br/><b>Research Library</b>
    </td>
    <td align="center">
      <img src="doc/screenshots/video_detail.png" alt="Video Detail & Insights" width="400"/>
      <br/><b>Video Detail & Insights</b>
    </td>
  </tr>
</table>

---

## 🏗️ Architecture

<p align="center">
  <img src="doc/assets/arc_diagram.png" alt="VidSage Architecture Diagram" width="800"/>
</p>

- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: FastAPI (Python), Node.js (Express), MongoDB & MySQL, Docker
- **AI/ML**: Gemini API, RAG (Retrieval-Augmented Generation) using LangChain
- **Authentication**: Clerk/Auth0 
- **Deployment**: Azure Container Apps & App Service

---

## 🛠️ Best Practices & Engineering Highlights


- **Microservices**: Modular FastAPI backend, clear separation of concerns
- **Type Safety**: TypeScript (frontend), Pydantic (backend)
- **DevOps**: Docker, environment configs, easy cloud/local deploy
- **Testing**: Automated unit & integration tests
- **CI/CD**: Automated build, test, deploy
- **AI**: Gemini API, LangChain RAG integration
- **OpenAPI**: Auto-generated docs & contracts
- **Security**: JWT, CORS, input validation, rate limiting
- **Performance**: Async, caching, vector search
- **Extensible**: Clean, pluggable codebase

> VidSage is engineered for reliability, scalability, and developer productivity—making it easy to extend, maintain, and deploy in real-world scenarios.

---

## 🌐 Live Demo

> [https://vidsage.com](https://vidsage-yt.web.app)

---

## 📚 API Documentation

- **Main API (Video Processing, Summaries, Q&A):**
  - Swagger/OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)

- **Tool Integration API (User Management, Google OAuth/Docs):**
  - Swagger/OpenAPI: [http://localhost:4000/docs](http://localhost:4000/docs)
  - OpenAPI YAML: [`backend/tool-integration/openapi.yaml`](backend/tool-integration/openapi.yaml)
