# Quick Start: AWS Configuration for OpenAg-DB

This guide provides a quick overview of setting up AWS infrastructure for OpenAg-DB. For detailed information, see [AWS_CONFIGURATION.md](AWS_CONFIGURATION.md).

## Prerequisites

- AWS account with admin access
- GitHub repository: `adam133/equipment-testing`
- AWS CLI installed and configured
- GitHub CLI (`gh`) installed (optional, for setting secrets)

## Quick Setup Steps

### 1. Create OIDC Provider (One-time setup)

```bash
# Set your AWS account ID
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create OIDC provider for GitHub Actions
# Note: The thumbprint value below is current as of this documentation.
# GitHub may rotate their SSL certificates, which would require updating this value.
# For dynamic thumbprint retrieval, see the Terraform examples using the tls_certificate data source.
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### 2. Create S3 Buckets

```bash
# Set your environment (dev or prod)
export ENVIRONMENT=prod
export AWS_REGION=us-east-1

# Create data lake bucket
aws s3 mb s3://openagdb-datalake-${ENVIRONMENT}-${AWS_REGION} --region ${AWS_REGION}

# Create artifacts bucket
aws s3 mb s3://openagdb-artifacts-${ENVIRONMENT}-${AWS_REGION} --region ${AWS_REGION}

# Enable versioning on data lake
aws s3api put-bucket-versioning \
  --bucket openagdb-datalake-${ENVIRONMENT}-${AWS_REGION} \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket openagdb-datalake-${ENVIRONMENT}-${AWS_REGION} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket openagdb-datalake-${ENVIRONMENT}-${AWS_REGION} \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 3. Create IAM Roles

See [AWS_CONFIGURATION.md](AWS_CONFIGURATION.md) for complete trust and permission policies.

**Required Roles:**
1. `GitHubActionsDeploymentRole-OpenAgDB` - For CI/CD deployments
2. `OpenAgDB-ScraperRole` - For data scrapers
3. `OpenAgDB-APIRole` - For Lambda API (future)

### 4. Configure GitHub Secrets

```bash
# Set these secrets in your GitHub repository
gh secret set AWS_ACCOUNT_ID --body "${AWS_ACCOUNT_ID}"
gh secret set AWS_REGION --body "us-east-1"
gh secret set AWS_DEPLOYMENT_ROLE_ARN --body "arn:aws:iam::${AWS_ACCOUNT_ID}:role/GitHubActionsDeploymentRole-OpenAgDB"
gh secret set AWS_SCRAPER_ROLE_ARN --body "arn:aws:iam::${AWS_ACCOUNT_ID}:role/OpenAgDB-ScraperRole"
gh secret set S3_DATALAKE_BUCKET --body "openagdb-datalake-${ENVIRONMENT}-${AWS_REGION}"
gh secret set S3_ARTIFACTS_BUCKET --body "openagdb-artifacts-${ENVIRONMENT}-${AWS_REGION}"
```

## Recommended Naming Convention

| Resource Type | Pattern | Example |
|--------------|---------|---------|
| Data Lake Bucket | `openagdb-datalake-<env>-<region>` | `openagdb-datalake-prod-us-east-1` |
| Artifacts Bucket | `openagdb-artifacts-<env>-<region>` | `openagdb-artifacts-prod-us-east-1` |
| IAM Role (Deployment) | `GitHubActionsDeploymentRole-OpenAgDB-<env>` | `GitHubActionsDeploymentRole-OpenAgDB-prod` |
| IAM Role (Scraper) | `OpenAgDB-ScraperRole-<env>` | `OpenAgDB-ScraperRole-prod` |
| IAM Role (API) | `OpenAgDB-APIRole-<env>` | `OpenAgDB-APIRole-prod` |

## Terraform Option

For infrastructure-as-code approach, see [terraform/README.md](terraform/README.md) for Terraform configuration examples.

```bash
cd terraform
terraform init
terraform plan -var-file="environments/prod/terraform.tfvars"
terraform apply -var-file="environments/prod/terraform.tfvars"
```

## Security Checklist

- [ ] OIDC provider configured for GitHub Actions
- [ ] IAM roles use OIDC (no long-lived credentials)
- [ ] S3 buckets have encryption enabled
- [ ] S3 buckets block public access
- [ ] S3 buckets have versioning enabled
- [ ] IAM policies follow least privilege principle
- [ ] Separate dev and prod environments
- [ ] CloudWatch logging enabled
- [ ] Environment variables set in GitHub secrets

## GitHub Secrets Summary

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCOUNT_ID` | Your AWS account ID | `123456789012` |
| `AWS_REGION` | Primary AWS region | `us-east-1` |
| `AWS_DEPLOYMENT_ROLE_ARN` | ARN of deployment role | `arn:aws:iam::123456789012:role/GitHubActionsDeploymentRole-OpenAgDB` |
| `AWS_SCRAPER_ROLE_ARN` | ARN of scraper role | `arn:aws:iam::123456789012:role/OpenAgDB-ScraperRole` |
| `S3_DATALAKE_BUCKET` | Data lake bucket name | `openagdb-datalake-prod-us-east-1` |
| `S3_ARTIFACTS_BUCKET` | Artifacts bucket name | `openagdb-artifacts-prod-us-east-1` |

## Next Steps

1. Review the complete [AWS Configuration Guide](AWS_CONFIGURATION.md)
2. Set up your AWS infrastructure (manual or Terraform)
3. Configure GitHub secrets
4. Test the scraper workflow: `.github/workflows/scraper.yml`
5. Deploy the API (when ready): `.github/workflows/deploy-api.yml.example`

## Troubleshooting

### OIDC Authentication Fails

- Verify OIDC provider exists in IAM
- Check role trust policy includes correct repository
- Ensure `id-token: write` permission in workflow

### S3 Access Denied

- Verify role has appropriate S3 permissions
- Check bucket policy doesn't deny access
- Ensure bucket names match in secrets and code

### Bucket Already Exists

- S3 bucket names are globally unique
- Choose a different name or use your AWS account ID in the name

## Support

For questions or issues, see the main [AWS_CONFIGURATION.md](AWS_CONFIGURATION.md) or open an issue on GitHub.
