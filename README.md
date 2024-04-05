# FastAPI: Photoshare

  Command #6 project from python WEB stream 18 GoIT
  

## Features

* Upload your own photos, images, posts as a pictures.

* Search all you pictures.

* Transform your posted pictures.

* Add up to 5 tags for each picture.

* Create comments under picture.

* Search pictures by tags.

* Rate pictures.

* Admin and Moderator functions

## Implemented functions

*  *Authentication*

	* JWT tokens

	* Administrator, moderator, and regular user roles

	* FastApi decorators are used to check the token and user role.

  

*  *Working with Pictures*
	* The main functionality of working with photos is performed using HTTP requests (POST, DELETE, PUT, GET, PATCH).

	* Unique tags for the entire application that can be added under a picture (up to 5 tags).

	* Users can perform basic actions with pictures allowed by the Cloudinary service.

	* Links for viewing a picture as a URL and QR-code can be created and stored on the server.

	* Administrators can perform all CRUD operations with user pictures.

  

*  *Commenting*
	* There is a block with comments under each picture.

	* The creation and editing time of the comment is stored in the database.

	* Users can only edit their comments but cannot delete them. Administrators and moderators can delete comments.
	


## Technologies

* Python 

* Fastapi 

* SQLAlchemy

* Alembic

* Pydantic

* Passlib

* Cloudinary / QRcode

* Pytest / Unittest

* PostgreSQL

* Swagger / Sphinx

  

# Instruction

## Installation

* The application code is available in the GitHub repository [repository](https://github.com/MariiaBulavina/GoIT-WEB-Project). The application is deployed at https://photo-share-marspace.koyeb.app/
  

## Usage

### Authorization

  

* Sign up page at the api/auth/signup page. For 1st user need admin access.

* After your succesfull sign up, admin can change your access or you can use app as user.

  

## About our team:

Team Lead/Developer: [Mariia Bulavina](https://github.com/MariiaBulavina)

Developer: [Sergiy Sobko](https://github.com/SobkoSergiy)

Developer: [Taras Miroshnichenko]()

Developer: [Roman Synyshyn](https://github.com/SRsr04)
