# Mastermind REST API  
![Project's coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)
## Index
1. [Introduction](#Introduction)
2. [Usage](#Usage)
3. [API documentation](#API%20documentation)
	3.1. [Open endpoints](#Open%20endpoints)
		- [Register user](#Register%20user)
		- [Obtain token](#Obtain%20token)
	3.2. [Authenticated endpoints](#Authenticated%20endpoints)
		-  [Create new game](#Create%20new%20game)
 		-  [Make guess](#Make%20guess)
 		-  [Show historic](#Show%20historic)
 		-  [Show guesses](#Show%20guesses)
 		-  [Show colours](#Show%20colours)
4. [Technologies used](#Technologies%20used)
## Introduction  

This is a REST API to play the [Mastermind](https://en.wikipedia.org/wiki/Mastermind_\(board_game\)) game made in Python 3.6 and Django 2.2.   

Its main features are:  
- REST API to play the basic (4 pegs per guess) Mastermind game.  
- Multiple users support, with automatic progress saving.  
- Historic of a users' games.  

## Usage  

This project is ready to be built and started using docker-compose. To build it, open a terminal in the root folder of the project and execute
  
```bash
docker-compose build
```

To start the containers, execute in the same folder  
```bash
docker-compose up
```  

Or, to execute both every time, just use  
```bash
docker-compose up --build
```  

After this, you will be ready to use the api, hosted at `localhost:8000`

There is also an admin to manage the users and have a more visual look at the games, accessible through your web browser in the `/admin/` endpoint. In order to enter, you will need superuser credentials. To create them, assuming you have your containers started, execute in another terminal in the root folder of the project
```bash
docker-compose exec backend ./manage.py createsuperuser
```

In order to test, execute in the same folder
```bash
docker-compose exec backend ./run_tests.py
```
This makes use of the `coverage` module to test and output a report on the percentage of code that has been tested. Its output at the current state of the project is 
```
Name					Stmts	Miss	Cover	Missing  
------------------------------------------------------  
game/choices.py			7		0 		100%  
game/models.py 			58 		0 		100%  
game/serializers.py 	22 		0 		100%  
game/urls.py 			3 		0 		100%  
game/utils.py 			8		0 		100%  
game/views.py 			43 		0 		100%  
mastermind/settings.py 	24 		0 		100%  
mastermind/urls.py 		6 		0 		100%  
users/models.py 		8 		0 		100%  
users/serializers.py 	14 		0 		100%  
users/urls.py 			3 		0 		100%  
users/views.py 			21 		0 		100%  
------------------------------------------------------  
TOTAL 					217 	0 		100%
```
Before committing changes to the project, it is important to detect and correct all non passing tests and formatting issues. In order to detect them, execute
```bash
flake8 --max-line-length=100 --exclude="*/migrations/*"
docker-compose exec backend ./run_tests.py
```

## API documentation
### Open endpoints
Open endpoints require no authentication
#### Register user
Registers a new user providing their username and password. In case of success, it returns the user's authorization token.
- **URL**
	`/api/users/`
- **Method**
	`POST`
- **JSON Content**
	```json
	{
		"username": string (required),
		"password": string (required)
	}
	```
- **Success response**
	- **Status code**: 201
	- **Response content**:  
		```json
		{"token": string}
		```
- **Error responses**
	- **Status code**: 400
	- **Response content**:
		```json
		"This user already exists"
		```
		OR
	- **Status code**: 400
	- **Response content**:
		```json
		{
			"username": [
		        "Enter a valid username. This value may contain only English letters, numbers, and @/./+/-/_ characters."
		    ]
		}
		```
		OR
	- **Status code**: 400
	- **Response content**:
		```json
		{
			"password": [
				"This password is too short. It must contain at least 8 characters."
			]
		}
		```
		OR
	- **Status code**: 400
	- **Response content**:
		```json
		{
			"password": [
				"This password is too common."
			]
		}
		```
		OR
	- **Status code**: 400
	- **Response content**:
		```json
		{
			"password": [
				"This password is entirely numeric."
			]
		}
		```

#### Obtain token
Obtains a user's token given its username and password.
- **URL**
	`/api/api-token-auth/`
- **Method**
	`POST`
- **JSON Content**
	```json
	{
		"username": string (required),
		"password": string (required)
	}
	```
- **Success response**
	- **Status code**: 200
	- **Response content**:  
		```json
		{"token": string}
		```
- **Error response**
	- **Status code**: 400
	- **Response content**:
		```json
		{
		    "non_field_errors": [
		        "Unable to log in with provided credentials."
		    ]
		}
		```
### Authenticated endpoints
In order to be able to access the following endpoints, the calls must have the header `Authorization:Token <A token obtained through any of the open endpoint calls>`. In case the token doesn't match one of an existing user, all these calls will return the following error response:
- **Status code**: 401
- **Response content**:
	```json
	{"detail": "Invalid token."}
	```
#### Create new game
Creates a new game for the user, finishing any saved game if there were any.
- **URL**
	`/api/new_game/`
- **Method**
	`POST`
- **JSON Content**
	```json
	{}
	```
- **Success response**
	- **Status code**: 201
	- **Response content**:  
		```json
		"New game created."
		```
#### Make guess
Makes a guess for the ongoing game, computing and returning the amount of white and black pegs there would be for this guess.
- **URL**
	`/api/make_guess/`
- **Method**
	`POST`
- **JSON Content**
	```json
	{
		"guess": [integer, integer, integer, integer] (required)
	}
	```
- **Success response**
	- **Status code**: 201
	- **Response content**:  
		```json
		{
		    "guess": [integer, integer, integer, integer],
		    "result_whites": integer,
		    "result_blacks": integer
		}
		```
- **Error response**
    - **Status code**: 400
	- **Response content**:
		```json
		"You have no started games yet."
		```
		OR
	- **Status code**: 400
	- **Response content**:
		```json
		{
		    "guess": {
			    "integer": [
					"Ensure this value is greater than or equal to 0."
				]
		    }
		}
		```
		OR
	- **Status code**: 400
	- **Response content**:
		```json
		{
		    "guess": {
			    "integer": [
					"Ensure this value is less than or equal to 6."
				]
		    }
		}
		```
		OR
	- **Status code**: 400
	- **Response content**:
		```json
		{
		    "guess": [
		        "This field must have 4 elements."
		    ]
		}
		```
#### Show historic
Shows an historic of the games played by the user, ordered from most recent to most recent to oldest, and returning for every game the amount of guesses made by the user, if the game has been finished and when it was last played.
- **URL**
	`/api/historic/`
- **Method**
	`GET`
- **Success response**
	- **Status code**: 200
	- **Response content**:  
		```json
		[
			{
				"guesses_count": integer,
				"finished": boolean;
				"updated": datetime
			},
			...
		]
		```
#### Show guesses
Shows the guesses made in the ongoing game, ordered from the last to the first one, returning for every guess the code given, the number of black pegs and the number of white pegs.
- **URL**
	`/api/guesses/`
- **Method**
	`GET`
- **Success response**
	- **Status code**: 200
	- **Response content**:  
		```json
		[
			{
				"guess": [integer, integer, integer, integer],
			    "result_whites": integer,
			    "result_blacks": integer
			},
			...
		]
		```
	- **Status code**: 400
	- **Response content**:
		```json
		"You have no started games yet."
		```
#### Show colours
Returns the possible colours to choose from to form a guess, with a string representation for each one of them.
- **URL**
	`/api/colours/`
- **Method**
	`GET`
- **Success response**
	- **Status code**: 200
	- **Response content**:  
		```json
		[
		    [0, "Green"], 
		    [1, "Blue"],
		    [2, "Red"],
		    [3, "Yellow"],
		    [4, "Purple"],
		    [5, "Orange"]
		]
		```
## Technologies used
- Python 3.6.8
- PostgreSQL 11.4

And the following python packages:
- coverage 4.5.3
- Django 2.2.2
- djangorestframework 3.9.4
- psycopg2-binary 2.8.3