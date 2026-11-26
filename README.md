# CAMPUS CONNECT
### Backend Application – Project Documentation

## 1. PROJECT OVERVIEW

**Project Name:** Campus Connect

**Description:**  
Campus Connect is a backend application designed to manage university clubs and campus events. Students can join clubs, register for events, and track their participation. Club coordinators can manage club activities, while administrators oversee the overall platform.

### Team Members and Contributions

| **Name** | **Roll Number** | **Endpoints Developed** |
|:---:|:---:|:---:|
| Madiha | AU25UG078 | E4, E5, E6, E7, E8, E9 |
| Aiman | AU25UG075 | E10, E11, E12, E13, E14, E15 |
| Shafreen | AU25UG079 | A1, A2, A3, E1, E2, E3 | 

## 2. LIVE APPLICATION

**API URL:** [(http://54.160.162.43:8001/)]
**API Docs:** [(http://54.160.162.43:8001/docs#/)]

**Default admin login:** `admin@campus.com` / `admin123`

## 3. HOW TO RUN THE APPLICATION LOCALLY

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Open http://127.0.0.1:8001/docs. The `data/` folder and the SQLite database are created automatically on first run.

## 4. DOCKER IMPLEMENTATION

Docker is used to containerize the backend so it runs the same way everywhere.

**Build the image** (from the project root):

```powershell
docker build -t campus-connect .
```

**Run the container:**

```powershell
docker run -d -p 8001:8001 -v ${PWD}/data:/app/data campus-connect
```

Open http://127.0.0.1:8001/docs.

**Note:** Stop any locally running Uvicorn server first, since both use port `8001`. The volume mapping keeps the database when the container is stopped or replaced.

## 5. DEPLOYMENT AND CI/CD PIPELINE

The application is deployed on an **AWS EC2 instance** using Docker and GitHub Actions.

### Deployment Workflow

1. **Code Push:** A push to the `main` branch triggers the GitHub Actions workflow.
2. **Docker Build:** GitHub Actions builds a new Docker image.
3. **Docker Hub:** The image is pushed to Docker Hub.
4. **EC2 Deployment:** GitHub Actions connects to EC2 over SSH, pulls the latest image and replaces the running container.
5. **Database Persistence:** The SQLite database is stored on the EC2 instance and mounted into the container.

### Database Volume Mapping

```bash
-v /home/ec2-user/campus-data:/app/data
```

### Deployment Summary

**GitHub → GitHub Actions → Docker Build → Docker Hub → AWS EC2 → Running Container**

Docker Hub credentials and EC2 SSH details are stored as GitHub Secrets.

## 6. API ENDPOINTS

Send the access token in a `token` header on every endpoint except A1–A3.

| # | Method | Endpoint | Access |
|:---:|:---:|:---|:---|
| A1 | POST | `/auth/register` | Public |
| A2 | POST | `/auth/login` | Public |
| A3 | POST | `/auth/refresh` | Public |
| E1 | POST | `/admin/coordinators` | Admin |
| E2 | POST | `/clubs` | Admin |
| E3 | GET | `/clubs` | Logged-in users |
| E4 | GET | `/clubs/{club_id}` | Logged-in users |
| E5 | PATCH | `/clubs/{club_id}` | Club coordinator |
| E6 | POST | `/clubs/{club_id}/apply` | Student |
| E7 | PATCH | `/clubs/{club_id}/requests/{request_id}` | Club coordinator |
| E8 | GET | `/clubs/{club_id}/members` | Club coordinator |
| E9 | POST | `/clubs/{club_id}/events` | Club coordinator |
| E10 | GET | `/events` | Logged-in users |
| E11 | POST | `/events/{event_id}/register` | Student |
| E12 | DELETE | `/events/{event_id}/register` | Student |
| E13 | PUT | `/events/{event_id}/attendance` | Club coordinator |
| E14 | GET | `/events/{event_id}/participants` | Club coordinator |
| E15 | GET | `/students/me/participation` | Student |

---

**END OF PROJECT DOCUMENTATION**
