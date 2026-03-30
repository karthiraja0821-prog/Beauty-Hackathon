# 💄 Ezhil-Sigai AI Salon Intelligence System
### *AI-Driven Precision for Authentic Beauty*

---

## 🚀 Overview
**Ezhil-Sigai** is a next-generation **AI-powered Salon Intelligence Platform** designed to transform traditional beauty services into **hyper-personalized digital experiences**.

It combines **AI analysis, customer profiling, predictive recommendations, and automation** to deliver intelligent beauty care across skin, hair, bridal styling, and salon operations.

---

## 🎯 Hackathon Alignment
This project addresses:

- **Hyper-Personalized Beauty Experiences**
- **AI Tools for Customer Engagement**
- **Salon Data → Business Intelligence**
- **Smart Automation & Predictive Insights**

---

## ✨ Key Features

### 🧠 AI Analysis Engine
- Skin tone & face analysis
- Hair health diagnostics
- Personalized beauty recommendations

### 👰 Bridal Intelligence System
- Saree-based look analyzer
- 3 priority bridal looks
- Jewellery + makeup + hairstyle suggestions
- Virtual bridal preview (simulation)

### 💬 Smart Chatbot (Tamil + English)
- Greets in Tamil first 🇮🇳
- Handles:
  - Hair care
  - Facials
  - Bridal services
  - Product recommendations

### 🦶 Foot Care AI
- Pressure-based analysis (simulated)
- Diabetic risk alerts
- Personalized care routines

### 🚨 Safety Alert Engine
- Incident tracking (INC001–INC010)
- Public safety scoring
- Risk alerts for salon environment

### 📊 Salon Intelligence Dashboard
- Customer beauty passport
- Loyalty tracking
- Revenue insights
- Seasonal trend analytics

---
## 🏗️ System Architecture
            +----------------------+
            |   User / Client App  |
            +----------+-----------+
                       |
                       v
            +----------------------+
            |   FastAPI Backend    |
            +----------+-----------+
                       |
    -----------------------------------------
    |            |            |              |
    v            v            v              v


## 🏗️ System ArchitectureAI Analysis Chatbot AI Safety Engine Bridal Engine
(Skin/Hair) (Tamil/Eng) (INC System) (Style Logic)
    -----------------------------------------
                       |
                       v
            +----------------------+
            |  Data & Insights     |
            | (Profiles, Reports)  |
            +----------------------+

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python)
- **AI/ML:**
  - Whisper (language/audio)
  - Librosa (audio features)
  - NumPy / Pandas
- **Visualization:** Matplotlib / Seaborn
- **Deployment Ready:** Uvicorn
- **API Security:** API Key validation

## ⚙️ How to Run
python -m uvicorn ezhilsigai:app --reload
pip install fastapi uvicorn scikit-learn requests pillow opencv-python numpy


### 1️⃣ Install dependencies
```bash
pip install fastapi uvicorn librosa numpy pandas matplotlib seaborn
