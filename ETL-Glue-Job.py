import boto3 # for connecting with aws services
import time
import pandas as pd
import numpy as np
from io import StringIO # for creating file-like object

AWS_ACCESS_KEY = "Enter Your AWS Access Key"
AWS_SECRET_KEY = "Enter Your AWS Secret Key"
AWS_REGION = "us-east-1"
SCHEMA_NAME = "dvdrental"
S3_STAGING_DIR = "s3://psp-dvdrental/output"
S3_BUCKET_NAME = "psp-dvdrental"
S3_OUTPUT_DIRECTORY = "output"

# connecting to athena
athena_client = boto3.client("athena",
                             aws_access_key_id=AWS_ACCESS_KEY,
                             aws_secret_access_key=AWS_SECRET_KEY,
                             region_name=AWS_REGION)

Dict = {}
def download_and_load_query_results(
    client: boto3.client, query_response: Dict) -> pd.DataFrame:
    while True:
        try:
            client.get_query_results(
                QueryExecutionId=query_response['QueryExecutionId'])
            break
        except Exception as err:
            if "not yet finished" in str(err):
                time.sleep(0.001)
            else:
                raise err
    temp_file_location: str = "athena_query_results.csv"
    # connecting to s3
    s3_client = boto3.client("s3",
                             aws_access_key_id=AWS_ACCESS_KEY,
                             aws_secret_access_key=AWS_SECRET_KEY,
                             region_name=AWS_REGION)
    s3_client.download_file(S3_BUCKET_NAME,
                            f"{S3_OUTPUT_DIRECTORY}/{query_response['QueryExecutionId']}.csv",
                            temp_file_location)
    return pd.read_csv(temp_file_location)

def query_table(table_name):
    response = athena_client.start_query_execution(
        QueryString=f"SELECT * FROM {table_name}",
        QueryExecutionContext={"Database": SCHEMA_NAME},
        ResultConfiguration={"OutputLocation": S3_STAGING_DIR,
                             "EncryptionConfiguration":{"EncryptionOption": "SSE_S3"}})
    return response

actor = download_and_load_query_results(athena_client, query_table("actor"))
film = download_and_load_query_results(athena_client, query_table("film"))
film_actor = download_and_load_query_results(athena_client, query_table("film_actor"))
category = download_and_load_query_results(athena_client, query_table("category"))
film_category = download_and_load_query_results(athena_client, query_table("film_category"))
store = download_and_load_query_results(athena_client, query_table("store"))
inventory = download_and_load_query_results(athena_client, query_table("inventory"))
rental = download_and_load_query_results(athena_client, query_table("rental"))
payment = download_and_load_query_results(athena_client, query_table("payment"))
staff = download_and_load_query_results(athena_client, query_table("staff"))
customer = download_and_load_query_results(athena_client, query_table("customer"))
address = download_and_load_query_results(athena_client, query_table("address"))
city = download_and_load_query_results(athena_client, query_table("city"))
country = download_and_load_query_results(athena_client, query_table("country"))
language = download_and_load_query_results(athena_client, query_table("language"))

# getting only the require columns from category table
dim_category = category[['category_id','name']]
# change column name 'name' to 'category'
dim_category.rename(columns={'name':'category'}, inplace=True)
dim_film_category = film_category[['film_id','category_id']]
dim_film_category_category = pd.merge(
    dim_film_category,dim_category, on='category_id', how='inner')

dim_film_actor = film_actor[['actor_id','film_id']]
dim_actor = actor[['actor_id','first_name','last_name']]
# change colum names
dim_actor.rename(columns={'first_name':'actor_first_name',
                          'last_name':'actor_last_name'}, inplace=True)
dim_film_actor_actor = pd.merge(dim_film_actor, dim_actor, on='actor_id', how='inner')

dim_film = film[['film_id','title','description','release_year','language_id',
                  'rental_duration','rental_rate','length',
                  'replacement_cost','rating']]
dim_language = language [['language_id','name']]
# change column names
dim_language.rename(columns={'name':'language'}, inplace=True)
dimFilm = pd.merge(dim_film, dim_language, on='language_id', how='inner')

dimFilm = pd.merge(dimFilm, dim_film_category_category, on='film_id', how='inner')
dimFilm = pd.merge(dimFilm, dim_film_actor_actor, on='film_id', how='inner')

#category,language,actor id remove
dimFilm.drop(['category_id','actor_id','language_id'], axis=1, inplace=True)
# rearrange columns
dimFilm = dimFilm[['film_id','title','category','description','release_year',
                   'language','actor_first_name','actor_last_name','rental_duration',
                   'rental_rate','length','replacement_cost','rating']]


dim_city = city[['city_id','city','country_id']]
dim_country = country[['country_id','country']]
dim_city_country = pd.merge(dim_city,dim_country, on='country_id', how='inner')

dim_address = address[['address_id','address','district','city_id','postal_code','phone']]
dim_address_city_country = pd.merge(dim_address, dim_city_country, on='city_id', how='inner')

dim_customer = customer[['customer_id','first_name','last_name','email',
                         'address_id','activebool','create_date','active']]
dimCustomer = pd.merge(
    dim_customer, dim_address_city_country, on='address_id', how='inner')

dimCustomer.drop(['address_id','city_id','country_id'], axis=1, inplace=True)
# rearrange columns
dimCustomer = dimCustomer[['customer_id','first_name','last_name','email','address',
                           'district','city','country','postal_code','phone',
                           'activebool','create_date','active']]


dim_store = store[['store_id','address_id']]
dim_store_address = pd.merge(
    dim_store, dim_address_city_country, on='address_id', how='inner')

# change columns name
dim_store_address.rename(columns={
    'address':'store_address','district':'store_district','city':'store_city',
    'country':'store_country','postal_code':'store_postal_code','phone':'store_phone'},
                         inplace=True)

dim_staff = staff[['staff_id','first_name','last_name','email',
                   'store_id','active','picture']]
dimStaff = pd.merge(dim_staff, dim_store_address, on='store_id', how='inner')

dimStaff.drop(['store_id','address_id','city_id','country_id'], axis=1, inplace=True)
# rearrange columns
dimStaff = dimStaff[['staff_id','picture','first_name','last_name','email',
                     'active','store_address','store_district','store_city',
                     'store_country','store_postal_code','store_phone']]


dimDate = payment[['payment_date']]
# spliting date and time into separate columns
dimDate[['date','time']] = dimDate.payment_date.str.split(' ',expand=True)
# inserting a column to use as primary key
dimDate.insert(0,'date_id',range(1,1+len(dimDate)))
# converting 'date' column data type into datetime format
dimDate['date'] = pd.to_datetime(dimDate['date'])
dimDate['day'] = dimDate['date'].dt.day
dimDate['day_of_week'] = dimDate['date'].dt.dayofweek
# Saturday = 5 and Sunday = 6 in day_of_week column
dimDate['is_weekend'] = np.where(dimDate['day_of_week'] >= 5, True, False)
dimDate['is_weekend'] = dimDate['is_weekend'].astype('str')
dimDate['month'] = dimDate['date'].dt.month
dimDate['year'] = dimDate['date'].dt.year

# create fact_date table to be use in creating factSales table
fact_date = dimDate[['date_id','payment_date']]

# remove payment_date and time columns
dimDate.drop(['payment_date','time'], axis=1, inplace=True)


fact_inventory = inventory[['inventory_id','film_id']]
fact_rental = rental[['rental_id','inventory_id']]
fact_rental_inventory = pd.merge(fact_rental, fact_inventory, on='inventory_id', how='inner')

fact_payment = pd.merge(payment, fact_rental_inventory, on='rental_id', how='inner')

# change columns name
fact_payment.rename(columns={'payment_id':'sales_id','amount':'sales_amount'}, inplace=True)
factSales = pd.merge(fact_payment, fact_date, on='payment_date', how='inner')

factSales.drop(['rental_id','inventory_id','payment_date'], axis=1, inplace=True)
# rearrange columns
factSales = factSales[['sales_id','staff_id','customer_id',
                      'film_id','date_id','sales_amount']]


s3_resource = boto3.resource('s3',
                             aws_access_key_id=AWS_ACCESS_KEY,
                             aws_secret_access_key=AWS_SECRET_KEY,
                             region_name=AWS_REGION)

transformed_tables = {'dimFilm':dimFilm, 'dimCustomer':dimCustomer,
                      'dimStaff':dimStaff, 'dimDate':dimDate,
                      'factSales':factSales}
for table_name, table in transformed_tables.items():
    csv_buffer = StringIO()
    table.to_csv(csv_buffer, index=False)
    s3_resource.Object(S3_BUCKET_NAME,f"transformed_tables/{table_name}.csv").put(Body=csv_buffer.getvalue())

# dimFilm schema
dimFilm_schema = pd.io.sql.get_schema(dimFilm.reset_index(drop=True),'dimFilm')
create_dimFilm = ''.join(dimFilm_schema)

# dimCustomer schema
dimCustomer_schema = pd.io.sql.get_schema(dimCustomer.reset_index(drop=True),'dimCustomer')
create_dimCustomer = ''.join(dimCustomer_schema)

# dimStaff schema
dimStaff_schema = pd.io.sql.get_schema(dimStaff.reset_index(drop=True),'dimStaff')
create_dimStaff = ''.join(dimStaff_schema)

# dimDate schema
dimDate_schema = pd.io.sql.get_schema(dimDate.reset_index(drop=True),'dimDate')
create_dimDate = ''.join(dimDate_schema)

# factSales schema
factSales_schema = pd.io.sql.get_schema(factSales.reset_index(drop=True),'factSales')
create_factSales = ''.join(factSales_schema)


import redshift_connector

redshift_user = "Enter Your Redshift User Name"
redshift_pass = "Enter Your Redshift Password"

conn = redshift_connector.connect(
    # endpoint of redshift cluster without port number and database name
    host='redshift-dvdrental.cmvn5zucztlv.us-east-1.redshift.amazonaws.com',
    database='dvdrental',
    user=redshift_user,
    password=redshift_pass)
conn.autocommit = True

cursor = redshift_connector.Cursor = conn.cursor()


create_tables = [create_dimFilm, create_dimCustomer,
                create_dimStaff, create_dimDate, create_factSales]
for table in create_tables:
    cursor.execute(f"""{table}""")

    
table_names = ['dimFilm','dimCustomer','dimStaff','dimDate','factSales']
for tablename in table_names:
    cursor.execute(f"""
    copy {tablename} from 's3://psp-dvdrental/transformed_tables/{tablename}.csv'
    delimiter ','
    credentials 'aws_iam_role=arn:aws:iam::276768453643:role/service-role/AmazonRedshift-CommandsAccessRole-20230126T181450'
    region 'us-east-1'
    IGNOREHEADER 1
    """)
conn.close()
