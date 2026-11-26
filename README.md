# CAMPUS CONNECT
### Backend Application – Project Documentation

## 1. PROJECT OVERVIEW

**Project Name:** Campus Connect

**Description:**  
Campus Connect is a backend application designed to manage university clubs and campus events. Students can join clubs, register for events, and track their participation. Club coordinators can manage club activities, while administrators oversee the overall platform.

### Team Members and Contributions

| Name | Roll Number | Endpoints Developed | 
|---|---|---|---|
| Madiha | AU25UG078 | E4, E5, E6, E7, E8, E9 |
| Aiman | AU25UG075 | E10, E11, E12, E13, E14, E15 | 
| Shafreen | AU25UG079 | A1, A2, A3, E1, E2, E3 | 

## 2. LIVE APPLICATION

**EC2 Deployment Link:**  
[Add your EC2 public URL here]

## 3. HOW TO RUN THE APPLICATION LOCALLY

### Backend Setup

**Step 1: Create the database directory**

The application stores its database inside the `C:\app\data` directory. Create this folder before running the backend.

```powershell
mkdir C:\app\data
```

**Step 2: Navigate to the backend directory**

```powershell
cd backend
```

**Step 3: Create a virtual environment**

```powershell
python -m venv venv
```

**Step 4: Activate the virtual environment**

```powershell
venv\Scripts\activate
```

**Step 5: Install the required dependencies**

```powershell
pip install -r requirements.txt
```

**Step 6: Set the SECRET_KEY environment variable**

```powershell
$env:SECRET_KEY = "any-key"
```

**Step 7: Start the FastAPI server**

```powershell
uvicorn main:app --reload --port 8001
```

**Step 8: Access the API documentation**

Open the following URL in your browser:

http://127.0.0.1:8001/docs

**Note:** The `SECRET_KEY` is not hardcoded in the application. It must be provided through an environment variable before starting the server. During EC2 deployment, it is securely provided using GitHub Secrets.

## 4. DOCKER IMPLEMENTATION

Docker is used to containerize the backend application, making it easier to run and deploy consistently across different environments.

### Step 1: Build the Docker Image

Run the following command from the project root directory:

```powershell
docker build -t campus-connect -f backend/dockerfile ./backend
```

### Step 2: Run the Docker Container

```powershell
docker run -d -p 8001:8001 -v ${PWD}/data:/app/data -e SECRET_KEY=any-key campus-connect
```

### Step 3: Access the Application

Open:

http://127.0.0.1:8001/docs

**Note:** Stop the locally running Uvicorn server before starting the Docker container, as both applications use port `8001`.

The Docker volume mapping ensures that database files remain available even when the container is stopped or replaced.

## 5. DEPLOYMENT AND CI/CD PIPELINE

The application is deployed on an **AWS EC2 instance** using Docker and GitHub Actions.

### Deployment Workflow

1. **Code Push:** Whenever changes are pushed to the `main` branch, the GitHub Actions workflow is triggered.
2. **Docker Build:** GitHub Actions automatically builds a new Docker image.
3. **Docker Hub:** The generated image is pushed to Docker Hub.
4. **EC2 Deployment:** The updated image is pulled and a new Docker container is launched on the EC2 instance.
5. **Database Persistence:** The database is stored on the EC2 instance at `/opt/feedback/data` and mounted into the container using a Docker volume.

### Database Volume Mapping

```bash
-v /opt/feedback/data:/app/data
```

This ensures that database data is preserved even when the existing Docker container is stopped or replaced.

### Deployment Summary

**GitHub → GitHub Actions → Docker Build → Docker Hub → AWS EC2 → Running Container**

**Note:** The `SECRET_KEY` is configured through GitHub Secrets and passed securely during deployment rather than being stored directly in the source code.

---

**END OF PROJECT DOCUMENTATION**
