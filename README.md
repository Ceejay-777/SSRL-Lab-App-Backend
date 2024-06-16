DATABASE/TASK MANAGEMENT WEB APPLICATION
-----
![Screenshot (39)](https://github.com/Faluyi/SSRL-SWEP-PROJECT/assets/83612442/b725f456-9845-4cce-9312-24965f2b58cb)

## Introduction

The data management system was designed for the Smart Systems Research Laboratory to allow users to enter and manage data, generate custom reports, and with a user-friendly interface

## Features
* UI/UX - a user-friendly and efficient UI/UX design for the data management system. 
* Data Model -  a data model to represent the laboratory's data which is stored in MongoDB. The data model is designed to be flexible and scalable to accommodate future changes.
* User Authentication - a user authentication system to ensure that only authorized users can access the application
* Data Entry 
* Data Management- allows users to managethe data in the system, including searching, filtering, update, etc. The application only allow users to view and edit their own data, and restrict access to other users' data based on their roles and permission
* Reporting
## Highlighted Features
* Personalized intern profiles introduced for efficient information
and task management.
* An admin-exclusive system for intern registration, role assignment, and stack classification.
* Automated generation of personalized user IDs and passwords, for enhancing the onboarding process.
* Role-specific access controls, outlining distinct admin, lead, and intern permissions.
* Streamlined task assignment using Ajax HTTP responses, ensuring a seamless user experience.

## Tech Stack (Dependencies)

### 1. Backend Dependencies
Our tech stack will include the following:
 * **virtualenv** as a tool to create isolated Python environments
 * **MONGODB** as our database of choice
 * **Python3** and **Flask** as our server language and server framework

> **Note** - If we do not mention the specific version of a package, then the default latest stable package will be installed. 

### 2. Frontend Dependencies
You must have the **HTML**, **CSS**, and **Javascript** with **BOOTSTRAP 5**

## Main Files: Project Structure

  ```sh
  ├── README.md
  └── db
      ├── models.py *** Database Models
  ├── static
  │   ├──images
  └── templates
      ├── forms
      ├── layouts
      └── pages
  ├── app.py *** the main driver of the app.
                    "python app.py" to run after installing dependencies
  ├── properties.py *** Database URI, ENV variables
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ```

Overall:
* Models are located in the 'models.py'
* Controllers are also located in `app.py`.
* The web frontend is located in `templates/`


4. **Install the dependencies:**
```
pip install -r requirements.txt
```

5. **Run the development server:**
```
python3 app.py
```
