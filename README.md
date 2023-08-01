# DjangoWeatherReminder

This Django Newsfeed API provides endpoints to interact with the newsfeed application's data. It allows authenticated users to retrieve, create, update, and delete subscriptions to cities.

### Usage
* configure ```.env``` file
* run application using docker compose: 
  ```
  docker compose up
  ```
  To use the API, make HTTP requests to the provided endpoints using your preferred HTTP client, such as curl or Postman.

### Endpoints

* __Create User__
    * URL: ```/api/auth/users/```
    * Method: POST
    * Parameters: username, password
    * Description: Create a new user with given username and password
* __Get JWT Token__
    * URL: ```/api/auth/jwt/create/```
    * Method: GET
    * Parameters: username, password
    * Description: Get JWT tokens with given username and password
* __Refresh JWT Token__
    * URL: ```/api/auth/jwt/refresh/```
    * Method: POST
    * Parameters: refresh JWT token
    * Description: Get access JWT token with given refresh token

* __Get Cities List__
    * URL: ```/api/cities/```
    * Method: GET
    * Permissions: Authenticated
    * Description: Retrieve a list of cities available in the system.
* __Get List of User Subscriptions__
    * URL: ```/api/subscriptions/```
    * Method: GET
    * Permissions: Authenticated
    * Description: Retrieve a list of subscriptions for the authenticated user.
* __Retrieve, Update, or Delete a Subscription__
    * URL: ```/api/subscriptions/{subscription_id}/```
    * Method: GET, PUT, PATCH, DELETE
    * Permissions: Admin or subscription owner
    * Description: Retrieve, update, or delete a specific subscription by providing its unique identifier (ID) in the URL.
* __Create a New Subscription__
    * URL: ```/api/subscribe/```
    * Method: POST
    * Permissions: Authenticated
    * Description: Create a new subscription for the authenticated user by sending a POST request with the required subscription data.
