# OneStopCarShop
The most comprehensive, data driven car shopping tool. 

Shopping for a new or used car can be a daunting task with how many webpages you need to traverse to find something that fits your interest; not to mention a vehicle is a significant investment. The intention of this project is to bring the power of data driven decision making that is available for organizations into the hands of the individual, allowing them to make a more informed, better decision regarding how to spend their money on a vehicle.

Cargurus does not have URLs that are easy to generate, making web scraping the site for listings extremely difficult. They make use of an "entitySelectingHelper" that has a unique ID for every make, model, and year combination. These IDs are also not stored anywhere that is easy to access. 

## Starting point for the project...
In its current state, the project consists of a few key pieces that are hosted on AWS.

- Web scraper
- MySQL Database
- REST API

The output of these is the ability to programmatically generate URLs on the Cargurus website such that they can scrape the pages for listings data. The web scraper scrapes the unique IDs used by Cargurus and stores them in a MySQL database. The REST API then queries the database for these IDs and returns them.

### Web Scraper
Cargurus does not have URLs that are easy to generate, making web scraping the site for listings extremely difficult. They make use of an "entitySelectingHelper" that has a unique ID for every make, model, and year combination. These IDs are also not stored anywhere that is easy to access. Additionally, these IDs are not part of the static HTML, making the use of the "requests" Python package not viable.

Introducing Selenium and headless-chromium! Headless chromium is a lightweight binary that is linux compatible. Since AWS Lambda does not come with Google Chrome pre-installed and requests won't get us the information we need, we need to use headless-chromium to function as a live browser from which we can extract the information needed.

The web scraper is a lambda function written in Python 3.X. The function and supporting functions were written outside of AWS Lambda in the PyCharm IDE and then zipped with the binary files. This zip was then uploaded to AWS Lambda.

The web scraper lambda function is scheduled to run once every month and can be manually triggered. It queries the table in the MySQL database and stores the table into a Pandas DataFrame. It then scrapes the Cargurus website for all of the unique Make IDs and compares the results with the DataFrame. If there are differences, then the new results are pushed to the table.

#### Note about Lambda Layers. 
All of the Python package dependencies were put into a Lambda Layer. The main reason for doing this was due to issues with NumPy and Pandas. These packages are dependent on the OS that compiles them. Since I work on a Windows machine and AWS Lambda runs on Linux, they were not compatible. Instead, I used AWS Cloud9 to pip install all package dependencies and save the environment as a Lambda Layer. The process was done using the following resource: https://towardsdatascience.com/python-packages-in-aws-lambda-made-easy-8fbc78520e30

### MySQL Database
Currently, there is only a "Makes" table that stores the unique Cargurus IDs and the names of each car make that it is associated with. The MySQL database and accompanying tables are hosted on an AWS RDS instance.

### REST API
The Rest API was created using AWS API Gateway. The API Gateway uses lambda integration and lambda proxy such that it can call an AWS Lambda function and pass it an event in the form of a JSON. 

An AWS Lambda function is used for returning results requested via the API's endpoint. When calling the API endpoint, parameters are passed in the URL which are passed to the event via "queryStringParameters". The lambda function then queries the table according to these parameters and returns a JSON output of all results that match.

## Special Thanks
Special thanks to the following resources for inspiration and guidance on how to complete this project:

Getting headless-chromium working on AWS Lambda - https://github.com/jairovadillo/pychromeless 
Creating Lambda Layers with dependencies installed - https://towardsdatascience.com/python-packages-in-aws-lambda-made-easy-8fbc78520e30
Creating a REST API using API Gateway and AWS Lambda - https://www.youtube.com/c/BeABetterDev/videos


