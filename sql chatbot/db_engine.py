import csv
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert,Float, Date,ForeignKey
from datetime import datetime # import datetime module

engine = create_engine('sqlite:///ssa_pdata.sqlite3', echo=True)



# Initialize metadata
metadata = MetaData()

# Define the table
my_table = Table(
    'jdd', metadata,
    Column('Primary', String, primary_key=True),
    Column('RPTG_PRD_ENDT',Date ),
    Column('FULLY_FAVORABLE', Float),
    Column('JUDGE', String),
    Column('HEARING_OFFICE',String ),
    Column('PARTIALLY_FAVORABLE',Float ),
    Column('REGION', Float),
    Column('TOTAL_ALJ_DIPOSITIONS_ACROSS_ALL_OFFICES',Float ),
    Column('TOTAL_AWARDS', Float),
    Column('TOTAL_DECISIONS',Float ),
    Column('RPTG_PRD_STDT',Date ),
    Column('TOTAL_DENIALS', Float),
    Column('TOTAL_DISPOSITIONS',Float )
)

my_table2 = Table(
    'fat', metadata,
    Column('HEARING_OFFICE',String, ForeignKey('jdd.HEARING_OFFICE')),
    Column('AVG_Ptime_RANK',Float ),
    Column('HEARING_OFFICE_TIMES_IN_MONTHS',Float ),
    Column('HO_CODE',Float ),
    Column('SITE_CODE',String , primary_key=True),
    Column('RPTG_PRD_ENDT',Date ),
    Column('ALJ_DISPS_PER_DAY_PER_ALJ', Float),
    Column('DISP_RANK', Float),
    Column('WORKDAYS', Float),
    Column('AVERAGE_PROCESSING_TIME', Float),
    Column('CASES_PENDING',Float ),
    Column('DISPOSITIONS:',Float ),
    Column('RECEIPTS', Float),
    Column('RPTG_PRD_STDT',Date )
)

# Create the table in the database
metadata.create_all(engine)

df = pd.read_csv('Administrative Law Judge Disposition Data updated.csv')

# Convert date strings to datetime objects
df['RPTG_PRD_ENDT'] = pd.to_datetime(df['RPTG_PRD_ENDT']).dt.date
df['RPTG_PRD_STDT'] = pd.to_datetime(df['RPTG_PRD_STDT']).dt.date

# Convert each row of the DataFrame to a dictionary and create a list of dictionaries
jdd = df.to_dict(orient='records')


df = pd.read_csv('df_main.csv')

# Convert date strings to datetime objects
df['RPTG_PRD_ENDT'] = pd.to_datetime(df['RPTG_PRD_ENDT']).dt.date
df['RPTG_PRD_STDT'] = pd.to_datetime(df['RPTG_PRD_STDT']).dt.date

# Convert each row of the DataFrame to a dictionary and create a list of dictionaries
fat = df.to_dict(orient='records')



# Insert multiple rows into the table using a batched insert
with engine.connect() as connection:
    stmt = insert(my_table)
    result = connection.execute(stmt, jdd)
    connection.commit()
    stmt2 = insert(my_table2) # create a new insert statement for the second table
    result2 = connection.execute(stmt2, fat) # execute insert for the second table
    connection.commit()