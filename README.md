App is ready to run in Django development mode on development server. 
There is also an option to build image and run Docker by using docker-compose.yml folder.
_______________________________
Instructions to run app locally:

! You have have Python 3.11 and pip installed on your device

1. Clone repo on your device by use command 'git clone github.com/lhreczuch/carfix_system_2025'
2. Go to /carfix_system_2025 and create local python environment in which you are going to install libraries. Instructions how to create and run local environment: https://docs.python.org/3/library/venv.html
3. Run command 'pip install -r requirements.py' in local environment
4. Run 'python car_fix_control_system/manage.py runserver' command to start app on Django development server.
5. App is going to be available on localhost port 8000.
6. You can log in by pre created user 'manager' with password '1'. Also if you want to log in to admin panel just use 'admin' user with password '1'.
