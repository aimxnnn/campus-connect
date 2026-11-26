1. Project and Team:

PROJECT NAME : campus-connect

A backend application for managing university clubs and campus events. Students can join clubs, register for events and track their participation. Club coordinators manage activities, while administrators manage the overall platform.

Team members:
Name	  Roll No   	Endpoints we built                     Other work
Madiha	AU25UG078	- endpoints - E4,E5,E6,E7,E8,E9           Readme
Aiman	AU25UG075	 -  endpoints - E10,E11,E12,E12,E14,E15
Shafreen AU25UG079 - endpoints - A1,A2,A3,E1,E2,E3

2. Live app:
   EC2 link :

3. How to run it
Backend
First create this folder because our database is saved inside it

mkdir C:\app\data
Then run these commands

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:SECRET_KEY = "any-key"
uvicorn main:app --reload --port 8001
Now open http://127.0.0.1:8001/docs

Note: we did not write the secret key in the code, so we have to give it in the terminal before running uvicorn. On EC2 it is taken from GitHub secrets.

4. Docker:
Run from the project folder

docker build -t feedback-api -f backend/dockerfile ./backend
docker run -d -p 8001:8001 -v ${PWD}/data:/app/data -e SECRET_KEY=any-key feedback-api
Now open http://127.0.0.1:8001/docs (stop uvicorn before this because both use port 8001)

5. Deployment:
Whenever we push to main branch, GitHub Actions builds the docker image, pushes it to Docker Hub and runs the new container on EC2. The database is stored in /opt/feedback/data on EC2 and connected to the container using -v /opt/feedback/data:/app/data, so old data is not lost when the container is replaced.

