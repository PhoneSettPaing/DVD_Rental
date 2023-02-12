# Data Modelling and Data Warehousing the DVD Rental Sample Database in AWS Redshift

## What is this Project about?
This Project is about migrating the require data from OLTP (Online Transaction Processing) system, a Relational Database into OLAP (Online Analytical Processing) system, a Data Warehouse for analytical purpose.

## Why migrate the data instead of directly doing analytics on OLTP system?
It is not a good idea to run analytic queries on Transactional Database as it might slow them down and have negative impacts on customers. This system is a critical system as it is serving the customers so it is a good idea to run analysis on a copy of this data in different database or a data warehouse to avoid any problems occurring in a critical system.

And running analytics queries on Transactional Database will be difficult and complex with multiple joints to tables as they usually store data in 3NF (Third Normal Form) form.

3NF is a database schema design approach for relational databases which uses normalizing principles to reduce the duplication of data and avoid data anomalies such as insert, update and delete anomalies.

Insert anomaly occurs when insertion of one record leads to the insertion of several more required data sets[^1].
![alt text](https://github.com/PhoneSettPaing/DVD_Rental/blob/3a926377db2ab83965c8cbfd232aca3362585fe9/images/Insert%20anomaly.PNG)
<p align='center'>Example College Enrolment Table for Insert Anomaly</p>

For example, I can enter a new course name in the above example college Enrolment Table but I can't add any new records until I enrol new students. And I can't enrol new students without assigning each student an ID. The Student ID column can't contain empty fields since it is a primary key. So, I can't insert a new course unless I insert new student data. I've encountered the insert anomaly problem.

Update anomaly occurs when updating a record in a table column requires further updates in other columns[^1].
![alt text](https://github.com/PhoneSettPaing/DVD_Rental/blob/87d26d871b383d9b79dae640d95f4198062ad6ba/images/Update%20anomaly.PNG)
<p align='center'>Example College Enrolment Table for Update Anomaly</p>

In the above Enrolment Table, the course and department information are repeated or duplicated for each student on that course. This duplication increases database storage and makes it more difficult to maintain data changes. A scenario in which Dr. Jones, the Director of the Computing Department, leaves his post and is replaced with another director, I will now need to update all instances of Dr. Jones in the table with the new Director's name. And I also need to update the records of every student enrolled in the department. This poses a major challenge because if I miss any students, then the table will contain inaccurate or inconsistent information. This is a prime example of the update anomaly problem. Updating data in one column requires updates in multiple others.

Delete anomaly occurs when deletion of one record leads to the deletion of several more required data sets[^1].
![alt text](https://github.com/PhoneSettPaing/DVD_Rental/blob/87d26d871b383d9b79dae640d95f4198062ad6ba/images/Delete%20anomaly.PNG)
<p align='center'>Example College Enrolment Table for Delete Anomaly</p>

For example, Rose, the student who has been assigned the ID of ‘04’ has decided to leave her course. So, I need to delete her data but deleting Rose's data results in the loss of the records for the design department as they're dependent on Rose and her ID. This is an example of the deletion anomaly problem. Removing one instance of a record of data causes the deletion of other records.

## Why use Data Warehouse?

Transactional Databases or Relational Databases are built to manage CRUD (Create, Read, Update, Delete) operations quickly by storing data as a row. They have a highly normalized data model. They focus on operational data and don’t always track historical information.

Data Warehouses are built to manage analytics and aggregations quickly by storing data as a columnar. Most of their data models are denormalized. They centralize and integrate business operations data and track historical information.
![alt text](https://github.com/PhoneSettPaing/DVD_Rental/blob/ddd0d6078022e7fcd6bf64f31eb5f9d049b1169f/images/Row_vs_Column_Store.png)
<p align='center'>Row Store Vs Column Store[^2]</p>
So, it is better to use a Data Warehouse for analytical purposes.
