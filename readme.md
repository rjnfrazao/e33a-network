# Project 4 - Network

## Hours

04/03 - Fri - 4h - Datamodel completed, Desing started, API needed defined, AllPages design started.
04/04 - Sat - 2:30 , started again at 15:00


## Design 

### Data Model

* Adding additional information to the user models, I decided to extend the AbstractUser
* Added to data staructure: 
    * UserProfile - Stores who the user follows. Relation one-to-one to the User model, and relation Many to Many with users models to store who this user follows.
    * Post - Stores the messages. Many to many relation to the User Model to keep the list of users who liked this post. It´s redundant, but I decided to add an attribute to keep the quantity of the likes of the post, this will keep the code simple and easy to mantain.

### Django Templates

* Django Layout.html template : Base template for all pages, it contains NavBar and all scripts plus stylesheets needed are loaded here.

* Index.html (inheret Layout.html) : Main page of the application, this pages will contain all pages of the applications, separeted by DIV elements, as the application will follow the desing partern of one page application.


### All Posts Page



* <div id=allposts> -> All posts page, this div  constains all elements needed on that page, this div is hide or unhide when needed, such as when clicking NavBar button "All Posts" unhide it.

    * <div id=post-form> -> Contains the form to post a message, the button of this form will call the javascript function post() responsible to fetch the API "/post" - responsible to save the post message.

    * <div id=post-list> -> React object responsible to render the list of posts as specified in the requirements.

