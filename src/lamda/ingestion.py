import boto3
import json
import os
import requests

from datetime import datetime


s3 = boto3.client('s3')
ssm = boto3.client('ssm')


def get_api_key():
    response = ssm.get_parameter(
        Name='/weather/api-key',
        WithDecryption=True
    )
    return response['Parameter']['Value']


def lambda_handler(event, context):

    # Allow EventBridge to pass different cities
    lat = event.get('lat', 53.34823)
    lon = event.get('lon', -6.25428)

    # Get API key from SSM
    api_key = get_api_key()

    # Make request to weather API
    url = 'http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{lon}&aqi=yes'

    try:
        response = requests.get(url.format(api_key=api_key, lat=lat, lon=lon))
        response.raise_for_status()  # check for HTTP errors
        data = response.json()
        now = datetime.now()
        location_name = data['location']['name']

        # Add metadata
        data['metadata'] = {
            'location': location_name,
            'timestamp': now.isoformat()
        }

        # Upload to S3
        bucket_name = os.environ['WEATHER_BRONZE_BUCKET_NAME']        
        # Organize by date for S3 Partitioning
        s3_path = f"data/place={location_name}/year={now.year}/month={now.month}/day={now.day}/weather_{now.strftime('%H%M%S')}.json"

        s3.put_object(
            Bucket=bucket_name,
            Key=s3_path,
            Body=json.dumps(data),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully stored weather for {location_name} at {s3_path}")
        }

    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error fetching weather data: {str(e)}")
        }
