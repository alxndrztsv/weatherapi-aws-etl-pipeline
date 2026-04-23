# Serverless AWS OpenWeather ETL Data Pipeline

## 1. Architecture Overview
**Ingestion:** Python Lambda triggered by EventBridge fetching data from WeatherAPI.  
**Storage:** S3 Medallion Architecture (Raw/Bronze $\rightarrow$ Processed/Silver).  
**Processing:** AWS Glue (PySpark) performing schema enforcement and Parquet conversion.  
**Orchestration:** AWS Step Functions managing the workflow dependencies.  
**Analytics:** Amazon Athena for serverless SQL querying.  

## 2. The Bronze Layer (Ingestion)
**Service:** AWS Lambda (Python 3.14).  
**Security:** API Keys stored securely in AWS Systems Manager (SSM) Parameter Store.  
**Partitioning Strategy:** Implemented Hive-style partitioning in S3 (place=P/year=Y/month=M/day=D/) to optimize query performance.  
**Key Challenge:** Initially encountered issues with simple folder paths; pivoted to Hive-style keys to enable automatic partition discovery in Spark.  

## 3. The Silver Layer (Processing)
**Service:** AWS Glue ETL (PySpark).  
- **Key Engineering Decisions:**  
  - **Manual Schema Definition:** Used `StructType` to enforce data quality and handle nested JSON structures (Air Quality, Location, Current, Condition).  
  - **Direct S3 Reading:** Bypassed the Data Catalog for the ETL input to eliminate "metadata lag" and reduce crawler costs.  
  - **File Format:** Converted raw JSON to Apache Parquet with Snappy compression to reduce storage costs and increase Athena query speed.  

## 4. Orchestration
**Service:** AWS Step Functions.  
**Logic Flow:** Lambda $\rightarrow$ Glue ETL $\rightarrow$ Silver Crawler.  
**Observability:** Integrated Amazon SNS to send real-time email alerts upon pipeline failure.  

## 5. Challenges & Solutions
**Challenge:** Schema Collision.  
**Solution:** Encountered a naming conflict between S3 partition keys and nested JSON fields (location). Resolved by renaming the internal Spark DataFrame alias to place.  

**Challenge:** Step Functions stalled indefinitely using "Wait for callback" (the Crawler doesn't support this). Conversely, unticking it caused the ETL job to read stale metadata before the Crawler finished.  
**Solution:** Pivoted to a decoupled architecture - bypassed the Bronze Crawler entirely by implementing a Manual Schema (StructType) in Spark. This allowed the ETL job to read directly from S3, ensuring 100% data consistency and less execution time.  

## 6. How to Run
Instructions on setting up the SSM Parameter.  
The Python code for the Lambda.  
The PySpark script for the Glue Job.  
The JSON definition for the Step Function.  



