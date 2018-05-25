# CPSC_476

# What I have learned
+ Understand characteristics of web applications and back-end technologies.
+ Apply database access techniques to persist data.
+ Evaluate characteristics of NoSQL databases and their influence on the design of web applications.
+ Gain experience with common web back-end tools and components.
+ Structure applications using server-side application patterns.
+ Assess the impact of various techniques for scaling applications.

# Outline of materials and concepts
+ Scalability and back-end concepts
+ Web Services and APIs
+ State Management and Load Balancing
+ Relational DBMSes and Data Models
+ NoSQL Databases
+ HTTP and Object Caching
+ Asynchronous Messaging
+ Software Engineering and Design
+ Running Services in Production

# Project 1
- From [original Minitwit source code](https://github.com/tngo0508/CPSC_476/tree/master/flask-original-version), I split it into separate indepdent pieces. I create a new Flask application mt_api.py that exposes RESTful URL endpoints for JSON data, rather than generating HTML. I create a file population.sql containing SQL INSERT statements to re-populate the database with test data.
- [Project 1 Instruction](https://github.com/tngo0508/CPSC_476/blob/master/Project_1/CPSC%20476%20-%20Spring%202018%20-%20Project%201.pdf)

# Project 2
- In this project, I refactor MiniTwit to use the Web Service API that you created in Project 1, then run multiple instances of both the front- and back-end servers behind a load balancer. In order to do this, I remove all references to sqlite3 and all database queries from minitwit.py, replacing them with requests to mt_api.py via the [Requests](http://docs.python-requests.org/en/master/) library.
- To simulate running MiniTwit in production, I run three instances of minitwit.py and three instances of mt_api.py. To do this, I create a [Procfile](http://blog.daviddollar.org/2011/05/06/introducing-foreman.html) and use the [foreman](http://ddollar.github.io/foreman/) command-line utility.
- To set up the load balancer, I use [NGINX](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-16-04)
- [Project 2 Instruction](https://github.com/tngo0508/CPSC_476/blob/master/Project_2/CPSC%20476%20-%20Spring%202018%20-%20Project%202.pdf)

# Project 3
- In this project, I port the MiniTwit API to [Cassandra](http://cassandra.apache.org/), a wide-column NoSQL database.
- [Project 3 Instruction](https://github.com/tngo0508/CPSC_476/blob/master/project_3/CPSC%20476%20-%20Spring%202018%20-%20Project%203.pdf)

# Project 4
- In this project, I add application-level sharding to MiniTwit, partitioning data across three SQLite databases.
- [Project 4 Instruction](https://github.com/tngo0508/CPSC_476/blob/master/Project_4/CPSC%20476%20-%20Spring%202018%20-%20Project%204.pdf)
