# Nombot with NuQui extension
A bot implementation for food tracking based on Telegram and the AIML standard.

### Setup
You need:
* Python 3.4
* Postgresql
* Telegram Bot token
* ngrok (just for local testing)

### Installation
Take case that you need Python 3.4 to make the nombot running. If you need a tool to manage your python versions we can recommand [pyenv](https://github.com/pyenv/pyenv).

#### Postgresql
Install postgresql ([for mac](https://gist.github.com/sgnl/609557ebacd3378f3b72))
Create a user called 'nombot' with the password 'feedme' and a database with the name nombot. The user 'nombot' should have been granted full rights on the 'nombot' database.

#### Get a telegram bot
Request a [telegram bot token](https://core.telegram.org/bots) (you can also use the given one)

#### Clone the repo
Go to a new folder and clone this repo
```
git clone git@github.com:nuqui-chatbot/nuqui-nombot.git
```

#### Install packages
Now we have to install all the dependencies. to do that move into the root folder of the nombot. You should have there a requirmenets.txt file. If thats not true, you are in the wrong folder :D. Then execute the following command:
```
pip install -r requirements.txt
```
This will need some seconds

Also we need to install the aiml module. Just move into the aimllib folder (nombot/aimllib/)and then install the module:
```
python setup.py install
```

#### Migrate database
Now we have to migrate the database (or create all the tables). Because we are running on the Django REST Framework we can just go to the root folder and start the migration process:
```
python manage.py migrate
```

#### Change settings
Now we need to adapt the settings of the bot. You can change the API token if you want (nombot/settings.py line 152) and you have to change the webhook URI. This is also done in the settings file (nombot/settings.py line 155) and you just need to enter your external URL +"/event". e.g. https://test.com/event
!!!IT NEEDS TO BE A https URL!!!

I you dont run it on a server you can use [ngrok](https://ngrok.com/download) to hide your external IP behind a domain.
If you have ngrok install you can just enter the following command:
```
ngrok http <Port>
```
This will start ngrok with your port (use 8000 because thats the default django one) and then you will get two forwards. Take the one with HTTPS and enter it into the settings file

#### Run the server for the first time
Now we can run the server for the first time and check if everything is working. You can start it with the command:
```
python manage.py runserver <Port>
```
Default will be 8000

Now you can go to localhost:8000/event and you should see a REST API page. If thats what you see, everythign is ok, else check the old installation guide (just below in the original notes)

#### Insert recipes and ingredients
So the server runs, but we dont need it at the moment so we can stop it with CTRL+C. Now we need to enter some data into the database and to make that easier for you we made an own repo with the data that has a script which will insert the data into the database. 
You just have to clone [this repo](https://github.com/nuqui-chatbot/nuqui-nombot-data) and then start the script:
```
python insert_script.py
```
And it will insert the recipes and the ingredients into the database.

#### Uncommend the /quiz part (test)
Then if you dont want to wait until the bot sends you a quiz you can go into the views file (nombot/views.py) and uncomment line 241-244. This will enable to call inside telegramm the command "/quiz" which will send you a quiz question. 
Then you can again start the bot and search it into telegram (if you didnt chaned the token you can look for NuQui)

### Usage
You can now chat with the bot (IN GERMAN) and tell him what you ate or get your score (/score). It will keep trak of your meal and weight but you are not able to use the plot function (see next chapter). 

### Changes to the original nombot
* We included the [NuQui extension](https://github.com/nuqui-chatbot/nuqui-quiz-extension) to the nombot
* Also we excluded the plot function because of problems with the plotterlibraries.

### Original notes:
This file contains setup and requirement notes for the project.

The server is implemented in Python using the Django Framework (https://www.djangoproject.com/) as the core framework for the webserver.

A number of libraries are used in conjunction with the server.

The libraries are listed in the requirements.txt file in the 'server/' directory.

The project runs on Python 3.4. The libraries can be installed using the pip package manager by running 'pip -r requirements.txt'


Additionally the library depends on the PyAIML3 library which can be found in theproject directory at 'server/pyaiml/'.
To install the library, run command 'python setup.py install' in the pyaiml directory.


The application uses the PostgreSQL Database system which has to be accessible on localhost:5432. The web server uses the database service as user 'nombot' with password 'feedme' and uses a database called 'nombot'. All these requirementshave to be met to enable the server using the database.

The user 'nombot' should have been granted full rights on the 'nombot' database.

The application registers a webhook at the Telegram bot api which pushes its messages over a secure HTTPS-Connection. To fully use the prototype, it has to be accessible over HTTPS-Connection with a valid SSL-Certificate.


The necessary database tables can be created by using the manage.py utility of the django server. 
The manage.py script can be found in the 'server/nombot' directory. To create the database migrations, run the command 'python manage.py makemigrations nombot'.

To apply the migrations to the database and create the necessary tables, run 'python manage.py migrate'.

To start up the server, run the command "python manage.py runserver <port>" while in the 'server/nombot' directory.
