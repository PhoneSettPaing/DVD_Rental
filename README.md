# Data Modelling and Data Warehousing the DVD Rental Sample Database in AWS Redshift
## What is this Project about?
This Project is about migrating the require data from OLTP(Online Transaction Processing) system,a Relational Database into OLAP(Online Analytical Processing) system,a Data Warehouse for analytical purpose using the data architecture below.
![Data Architecture](https://github.com/PhoneSettPaing/DVD_Rental/blob/b8e9287e20fd546f23e64e5e2284b3a27e3a3d60/images/Data_Architecture.PNG)
<p align='center'>Data Architecture</p>

## Why migrate the data instead of directly doing analytics on OLTP system?
It is not a good idea to run analytic queries on Transactional Database as it might slow them down and have negative impacts on customers. This system is a critical system as it is serving the customers so it is a good idea to run analysis on a copy of this data in different database or a data warehouse to avoid any problems occurring in a critical system.

And running analytics queries on Transactional Database will be difficult and complex with multiple joints to tables as they usually store data in 3NF(Third Normal Form) form.

3NF is a database schema design approach for relational databases which uses normalizing principles to reduce the duplication of data and avoid data anomalies such as insert, update and delete anomalies.

Insert anomaly occurs when insertion of one record leads to the insertion of several more required data sets[^1].
![Insert Anomaly Table](https://github.com/PhoneSettPaing/DVD_Rental/blob/3a926377db2ab83965c8cbfd232aca3362585fe9/images/Insert%20anomaly.PNG)
<p align='center'>Example College Enrolment Table for Insert Anomaly</p>

For example, I can enter a new course name in the above example college Enrolment Table but I can't add any new records until I enrol new students. And I can't enrol new students without assigning each student an ID. The Student ID column can't contain empty fields since it is a primary key. So, I can't insert a new course unless I insert new student data. I've encountered the insert anomaly problem.

Update anomaly occurs when updating a record in a table column requires further updates in other columns[^1].
![Update Anomaly Table](https://github.com/PhoneSettPaing/DVD_Rental/blob/87d26d871b383d9b79dae640d95f4198062ad6ba/images/Update%20anomaly.PNG)
<p align='center'>Example College Enrolment Table for Update Anomaly</p>

In the above Enrolment Table, the course and department information are repeated or duplicated for each student on that course. This duplication increases database storage and makes it more difficult to maintain data changes. A scenario in which Dr. Jones, the Director of the Computing Department, leaves his post and is replaced with another director, I will now need to update all instances of Dr. Jones in the table with the new Director's name. And I also need to update the records of every student enrolled in the department. This poses a major challenge because if I miss any students, then the table will contain inaccurate or inconsistent information. This is a prime example of the update anomaly problem. Updating data in one column requires updates in multiple others.

Delete anomaly occurs when deletion of one record leads to the deletion of several more required data sets[^1].
![Delete Anomaly Table](https://github.com/PhoneSettPaing/DVD_Rental/blob/87d26d871b383d9b79dae640d95f4198062ad6ba/images/Delete%20anomaly.PNG)
<p align='center'>Example College Enrolment Table for Delete Anomaly</p>

For example, Rose, the student who has been assigned the ID of ‘04’ has decided to leave her course. So, I need to delete her data but deleting Rose's data results in the loss of the records for the design department as they're dependent on Rose and her ID. This is an example of the deletion anomaly problem. Removing one instance of a record of data causes the deletion of other records.

## Why use Data Warehouse?
Transactional Databases or Relational Databases are built to manage CRUD(Create, Read, Update, Delete) operations quickly by storing data as a row. They have a highly normalized data model. They focus on operational data and don’t always track historical information.

Data Warehouses are built to manage analytics and aggregations quickly by storing data as a columnar. Most of their data models are denormalized. They centralize and integrate business operations data and track historical information.
![Row Store Vs Column Store](https://github.com/PhoneSettPaing/DVD_Rental/blob/ddd0d6078022e7fcd6bf64f31eb5f9d049b1169f/images/Row_vs_Column_Store.png)
<p align='center'><cite><a href="http://www.hanaexam.com/p/row-store-vs-column-store.html">Row Store Vs Column Store</a></cite></p>
So, it is better to use a Data Warehouse for analytical purposes.

## Things I have done in this Project:
In this Project, I used DVD rental data form [PostgreSQL Sample Database(postgresqltutorial.com)](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/) as an example data source, PostgreSQL as a Database for OLTP system and AWS Redshift as a Data Warehouse for OLAP system.

I have downloaded the PostgreSQL DVD Rental sample database and restored it into a database created on PostgreSQL server. Then I exported all the tables from the database to local storage in csv file format.

After that I created an AWS S3(Simple Storage Service) bucket, a cloud storage and uploaded those csv files into that bucket.

I created and run a crawler in AWS Glue(a serverless data integration service that makes it easy for analytics users to discover, prepare, move, and integrate data from multiple sources) to populate the Data Catalog in AWS Glue with metadata tables of those csv files in the AWS S3 bucket.

A crawler is a job defined in AWS Glue. It crawls databases and buckets in S3 to creates metadata tables in Data Catalog together with their schema. The metadata tables that a crawler creates are contained in a database(a container of tables in the Data Catalog) when you define a crawler.

The AWS Glue Data Catalog is a persistent technical metadata store. It is a managed service that can be use to store, annotate, and share metadata in the AWS Cloud.

Then I used AWS Athena(an interactive query service that makes it easy to analyse data in AWS S3 using standard SQL) to query the uploaded tables in S3 for checking and comparing with tables in the PostgreSQL Database to find out if there were any mismatch or error in data when uploading them onto S3. AWS Athena query data place in S3 using the database and metatables in AWS Glue Catalog. I also use AWS Athena to get Tables’ Structure to create star schema data model for Data Warehouse, AWS Redshift.

Data Warehouse is schema on write which means it needs to have a schema before loading data into it. Data Warehouse usually have snowflake or star schema and these tables are very structured which means that it is not very flexible and it is very rigid, thus changing it is slow.

Since it is a schema on write, I created a star schema data model before uploading data into a Data Warehouse, Redshift.

![ER Diagram](https://github.com/PhoneSettPaing/DVD_Rental/blob/1def632018be3434417b30349ecf62fa79d5afaf/images/dvdrental_ER_diagram.PNG)
<p align='center'>Orginal DVD Rental ER(Entity Relationship) Model</p>

![Star Schema](https://github.com/PhoneSettPaing/DVD_Rental/blob/1def632018be3434417b30349ecf62fa79d5afaf/images/dvdrental_star_schema.PNG)
<p align='center'>DVD Rental Star Schema Model I have created</p>

After that I created a cluster and then a database in that cluster on Redshift. Later that database will get uploaded with tables from the above star schema.

I have written [ETL job in Jupyter Notebook](https://github.com/PhoneSettPaing/DVD_Rental/blob/1def632018be3434417b30349ecf62fa79d5afaf/ETL.ipynb) and run it to Extract tables from S3 using Athena, Transform the tables’ structure into the structure define in the created star schema, save the transformed tables back into S3 and then Load them into a Redshift from S3.

I have also done another way of loading data into Redshift which is writing [ETL script](https://github.com/PhoneSettPaing/DVD_Rental/blob/1def632018be3434417b30349ecf62fa79d5afaf/ETL-Glue-Job.py), then creating and running a Job in AWS Glue Studio (A graphical interface that makes it easy to create, run, and monitor extract, transform, and load (ETL) jobs in AWS Glue) by uploading that ETL script.

After loading the data, I connected Redshift with Tabelau(Data visualization software) to create a sample dashboard business report.
![Example Dashboard](https://github.com/PhoneSettPaing/DVD_Rental/blob/1def632018be3434417b30349ecf62fa79d5afaf/images/DVD_Rental_Dashboard.PNG)
<p align='center'>Sample Dashboard I created using Tableau</p>

## Step for following this Project:
1.	Create a database in PostgreSQL and Restore DVD Rental Sample Database in that database then Export tables in the database as csv format including headers.

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=oQnMNqjHm34" target="_blank"><img src="http://img.youtube.com/vi/oQnMNqjHm34/0.jpg"></a></p>
<p align='center'>Video example of Creating & Restoring database in PostgreSQL and Exporting tables in database as csv</p> 

2.	Create an AWS S3 bucket and Upload tables data into that bucket

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=-E-xIFnsfNM" target="_blank"><img src="http://img.youtube.com/vi/-E-xIFnsfNM/0.jpg"></a></p>

3.	Create and Run a Crawler in AWS Glue

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=VqkqZCmJ_rU" target="_blank"><img src="http://img.youtube.com/vi/VqkqZCmJ_rU/0.jpg"></a></p>

4.	Query the Tables uploaded into S3 and also Get Tables’ Structure with Athena

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=F90ausRTD-0" target="_blank"><img src="http://img.youtube.com/vi/F90ausRTD-0/0.jpg"></a></p>

5.	Create a Redshift cluster and a database in that cluster

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=ja2XDOZQjs4" target="_blank"><img src="http://img.youtube.com/vi/ja2XDOZQjs4/0.jpg"></a></p>

6.	Run ETL in Jupyter Notebook

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=kft4Pa_CDB0" target="_blank"><img src="http://img.youtube.com/vi/kft4Pa_CDB0/0.jpg"></a></p>

7.	Create an IAM Role for AWS Glue Job

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=IU00ZfbAVYg" target="_blank"><img src="http://img.youtube.com/vi/IU00ZfbAVYg/0.jpg"></a></p>

8.	Create an ETL Job in AWS Glue Studio

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=PwBuIOGkh0c" target="_blank"><img src="http://img.youtube.com/vi/PwBuIOGkh0c/0.jpg"></a></p>

9.	Run an ETL Glue Job

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=Ll9cgAr8dxU" target="_blank"><img src="http://img.youtube.com/vi/Ll9cgAr8dxU/0.jpg"></a></p>

10.	Connect Tableau with Redshift

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=_Ou1YjPEGSE" target="_blank"><img src="http://img.youtube.com/vi/_Ou1YjPEGSE/0.jpg"></a></p>

11.	Create a dashboard in Tableau 

<p align='center'><a href="http://www.youtube.com/watch?feature=player_embedded&v=-VpiOZkBrgU" target="_blank"><img src="http://img.youtube.com/vi/-VpiOZkBrgU/0.jpg"></a></p>

[^1]: [Meta's Course 'Introduction to Database' in Coursera](https://www.coursera.org/learn/introduction-to-databases/lecture/ToTaE/what-is-database-normalization).
