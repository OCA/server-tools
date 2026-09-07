## AWS SES Setup

1. Verify your domain in AWS SES (e.g., `docs.example.com`)
2. Add MX record: `docs.example.com MX 10 inbound-smtp.us-east-1.amazonaws.com`
3. Create an SES receipt rule that stores emails in an S3 bucket
4. Create an IAM user with `s3:GetObject`, `s3:ListBucket`, `s3:DeleteObject`,
   `s3:PutObject` permissions on the bucket

## Odoo Configuration

1. Go to **Settings → Technical → Incoming Mail Servers**
2. Create a new server with type **S3 Bucket**
3. Fill in:
   - **S3 Bucket Name**: your bucket (e.g., `my-ses-incoming`)
   - **Object Key Prefix**: the prefix SES writes to (e.g., `emails/`)
   - **AWS Region**: the bucket's region (e.g., `us-east-1`)
   - **Access Key ID** and **Secret Access Key**: IAM credentials
   - **Endpoint URL**: leave empty for AWS S3, or set for S3-compatible services
   - **Archive Prefix**: where to move processed emails (e.g., `processed/`).
     Leave empty to delete after processing.
4. Click **Test & Confirm** to verify connectivity
5. Set the **Create a New Record** model (e.g., DMS Directory for document filing)
