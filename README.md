# Data Modelling and Data Warehousing the DVD Rental Sample Database in AWS Redshift

## What is this Project about?
This Project is about migrating the require data from OLTP (Online Transaction Processing) system, a Relational Database into OLAP (Online Analytical Processing) system, a Data Warehouse for analytical purpose.

## Why migrate the data instead of directly doing analytics on OLTP system?
It is not a good idea to run analytic queries on Transactional Database as it might slow them down and have negative impacts on customers. This system is a critical system as it is serving the customers so it is a good idea to run analysis on a copy of this data in different database or a data warehouse to avoid any problems occurring in a critical system.

And running analytics queries on Transactional Database will be difficult and complex with multiple joints to tables as they usually store data in 3NF (Third Normal Form) form.

3NF is a database schema design approach for relational databases which uses normalizing principles to reduce the duplication of data and avoid data anomalies such as insert, update and delete anomalies.

Insert anomaly occurs when insertion of one record leads to the insertion of several more required data sets.
![alt text](https://github.com/PhoneSettPaing/DVD_Rental/blob/3a926377db2ab83965c8cbfd232aca3362585fe9/images/Insert%20anomaly.PNG)
