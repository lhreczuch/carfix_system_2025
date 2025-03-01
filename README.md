# [INSTRUCTIONS HOW TO RUN APP ARE PLACED DOWN BELOW THIS DESCRIPTION]

carfix_system is project in Django that I was working on since 6.2024 up to 10.2024.
It is an app to help organise work in car repair service. I build this app using Django, Django Rest Framework, HTML and CSS.
Main functional / non-functional requirements were:
- there should be authorization process
- there should 3 groups of users with specific privilleges - manager, worker, client
- make it possible for organisation to store data about their everyday work. By that I mean storing data in database about repairs, cars, clients, and precise informations about repairs (who and when did what on specific repair)
- make it possible to log work on specific repair by workers
- managers should be able to assign repairs to specific workers
- there should be an option to easily generate repair reports in .pdf or .csv
- workers should be able to manage repair statuses
- clients should receive email with repair status after it is done
- there should be an API to integrate app with other company apps or build mobile app based on models from this app.

# Main things I learned during creating this App.

1. I got familiar with Postman when I was testing my API and got familiar with GIT - was creating commits in dedicated repo all the time during process.
2. I learned how to build api with REST rules and how to secure it using JWT token and specify permissions using permission classes.
3. I learned how to build API docs using OpenAPI
4. I learned how to operate on manytomany database relations in Django 
5. I learned how to restrict data rendered by server to web browser based on which user is logged currently logged In. User and its privilleges are being checked on views.py file functions on server side.
6. I became more comfortable with Django built in model methods like save(), django signals,forms or serializers. Also i got familiar with django errors in debug mode - I recognize them and I'am able to debug many of them without searching web.

# Running App
### -> App is ready for you to run in Django development mode on development server. 
### -> There is also an option to build image and run Docker by using docker-compose.yml folder.
_______________________________
Instructions to run app locally:

! You have have Python 3.11 and pip installed on your device

1. Clone repo on your device by use command 'git clone github.com/lhreczuch/carfix_system_2025'
2. Go to /carfix_system_2025 and create local python environment in which you are going to install libraries. Instructions how to create and run local environment: https://docs.python.org/3/library/venv.html
3. Run command 'pip install -r requirements.py' in local environment
4. Run 'python car_fix_control_system/manage.py runserver' command to start app on Django development server.
5. App is going to be available on localhost port 8000.
6. You can log in by pre created user 'manager' with password '1'. Also if you want to log in to admin panel just use 'admin' user with password '1'.

_______________________________
Instructions to run app using Docker:

! You have have Docker installed on your device and have a Docker engine running.

1. Clone repo on your device by use command 'git clone github.com/lhreczuch/carfix_system_2025'
2. Go to /carfix_system_2025 and run 'docker-compose up' or 'docker compose up'
3. App is going to be available on port 80 on your device. If you want to change port used on your device change port setting in docker-compose.yml to [your_local_desired_port]:80 and build app again.

### You can access api docs after running app on /api/docs endpoint. You have to authorize with JWT token to see all API endpoints.
