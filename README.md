# AnimeKaisen Telegram Bot

Production-ready Telegram card battle game deployed in the cloud with a DevOps-focused stack.

- **Bot:** [@AnimeKaisenbot](https://t.me/AnimeKaisenbot)
- **Channel:** [@multiverse_card](https://t.me/multiverse_card)
- **Users:** ~2000

---

## ✨ Features

- 🃏 Card collection system
- ⚔️ PvP and PvE battles
- 🤖 AI opponents
- 🎴 Gacha mechanics
- 🏆 Economy and progression
- 🐉 Boss fights
- 🏰 Clan system
- 📈 Player statistics
- 🎮 Automated battle logic

---

## 🏗 Architecture

```text
Telegram API
    │
    ▼
aiogram bot
    │
    ▼
Kubernetes (k3s on AWS EC2)
    │
    ▼
MongoDB Atlas
    │
    ├── Prometheus (metrics)
    └── Grafana (dashboards)
```

---

## 🧰 Tech Stack

### Backend

- Python 3
- aiogram

### Database

- MongoDB Atlas

### Infrastructure

- Docker
- Kubernetes (k3s)
- AWS EC2

### CI/CD

- GitLab CI/CD (build/deploy pipeline)
- GitHub (portfolio mirror repository)

### Monitoring

- Prometheus
- Grafana

---

## ☁️ Production Infrastructure

The bot is deployed in production on **AWS EC2** and runs in **Kubernetes (k3s)**.

### What is configured

- Dockerized application
- Kubernetes deployment/service
- Production bot runtime on EC2
- Prometheus metrics collection
- Grafana dashboards for monitoring
- MongoDB Atlas as managed cloud database

---

## 🗄 Database (MongoDB Atlas)

The project uses **MongoDB Atlas** to store game data, including:

- user profiles
- characters/cards
- battle data
- economy/progression
- player statistics

---

## 🔌 Networking & Ports

### Local Docker run (example)

```bash
docker run -d -p 8000:8000 animekaisen
```

### Kubernetes exposure options

- `Service` (`ClusterIP` / `NodePort`)
- `Ingress` (optional)
- port forwarding for debugging:

```bash
kubectl port-forward svc/<service-name> 8000:8000 -n <namespace>
```

---

## 🐳 Local Development

### 1) Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/animekaisen.git
cd animekaisen
```

### 2) Create environment file

```bash
cp .env.example .env
```

### 3) Run locally

```bash
docker compose up --build
```

---

## 🚀 CI/CD Notes

- Main working deployment pipeline is connected to **GitLab** (auto deploy on push).
- A separate **GitHub repository** can be used as a portfolio mirror for public showcase.

> If needed, add a second remote and push to both platforms.

```bash
git remote -v
# add GitHub remote example:
# git remote add github https://github.com/<username>/<repo>.git
# git push github main
```

---

## 📊 DevOps Highlights

This project demonstrates:

- production deployment
- containerization
- Kubernetes orchestration
- CI/CD pipeline setup
- cloud infrastructure on AWS
- monitoring & observability (Prometheus + Grafana)

---

## 🎯 Project Goal

This project is used as a **portfolio project** to demonstrate real-world experience in building and operating a production service (Backend + DevOps).

---

## 📜 License

MIT