# Multi-tenancy with AWS Transfer Family

The templates in this folder are created as part of the blogpost [How Multi-Tenancy with AWS Transfer Family is a Cost-Effective Solution](https://aws.amazon.com/blogs/apn/how-multi-tenancy-with-aws-transfer-family-is-a-cost-effective-solution/)

## Templates
- `server.yaml` will create an AWS Transfer Family SFTP Server, with an Amazon Simple Storage Server (Amazon S3) bucket as storage and an AWS Identity and Access Management (IAM) role to allow access from the server to the bucket.
- `user.yaml` will create a user (in AWS Transfer Famliy) that can access (only) its own folder/data in the shared server and bucket.

## Deployment
`server.yaml` should be deployed first and only once, you can deploy `user.yaml` multiple times after that.
