import boto3
import json
from datetime import datetime
import os

class S3DataService:
    """Store and retrieve historical risk data using AWS S3"""

    def __init__(self, bucket_name=None, region='us-east-1'):
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME', 'heat-water-stress-data')
        self.region = region
        self.s3_client = None

        # Only initialize S3 client if credentials are available
        try:
            self.s3_client = boto3.client('s3', region_name=region)
        except Exception as e:
            print(f"S3 client initialization failed: {e}")
            print("Running in local mode without S3")

    def save_risk_data(self, risk_data, location_id=None):
        """Save risk assessment data to S3"""
        if not self.s3_client:
            # Local mode: save to file
            return self._save_local(risk_data, location_id)

        timestamp = datetime.now().isoformat()
        key = f"risk-assessments/{location_id or 'unknown'}/{timestamp}.json"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(risk_data),
                ContentType='application/json'
            )
            return {'success': True, 'key': key}
        except Exception as e:
            print(f"Error saving to S3: {e}")
            return self._save_local(risk_data, location_id)

    def get_historical_data(self, location_id, days=7):
        """Retrieve historical risk data for a location"""
        if not self.s3_client:
            # Local mode: read from file
            return self._get_local_historical(location_id, days)

        try:
            prefix = f"risk-assessments/{location_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            if 'Contents' not in response:
                return []

            # Get the most recent entries
            objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)[:days*24]

            historical_data = []
            for obj in objects:
                obj_response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                data = json.loads(obj_response['Body'].read())
                historical_data.append(data)

            return historical_data
        except Exception as e:
            print(f"Error fetching from S3: {e}")
            return []

    def _save_local(self, risk_data, location_id):
        """Save data locally for demo mode"""
        os.makedirs('local_data/risk-assessments', exist_ok=True)
        timestamp = datetime.now().isoformat()
        filename = f"local_data/risk-assessments/{location_id or 'unknown'}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(risk_data, f)

        return {'success': True, 'key': filename}

    def _get_local_historical(self, location_id, days):
        """Get local historical data for demo mode"""
        import glob
        pattern = f"local_data/risk-assessments/{location_id or 'unknown'}_*.json"
        files = glob.glob(pattern)

        historical_data = []
        for file in sorted(files, reverse=True)[:days*24]:
            with open(file, 'r') as f:
                historical_data.append(json.load(f))

        return historical_data
