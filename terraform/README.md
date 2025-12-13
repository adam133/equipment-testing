# Terraform Configuration Examples for OpenAg-DB

This directory contains example Terraform configurations for provisioning AWS infrastructure for OpenAg-DB.

## Prerequisites

- Terraform >= 1.5.0
- AWS CLI configured
- GitHub repository: `adam133/equipment-testing`

## Quick Start

```bash
# Initialize Terraform
terraform init

# Plan infrastructure changes
terraform plan -var-file="environments/prod/terraform.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/prod/terraform.tfvars"
```

## Directory Structure

```
terraform/
├── README.md                    # This file
├── main.tf                      # Root module
├── variables.tf                 # Input variables
├── outputs.tf                   # Output values
├── versions.tf                  # Provider versions
├── modules/
│   ├── s3-buckets/             # S3 bucket module
│   ├── iam-oidc/               # GitHub OIDC provider module
│   ├── iam-roles/              # IAM roles module
│   └── cloudwatch/             # CloudWatch monitoring module
└── environments/
    ├── dev/
    │   └── terraform.tfvars    # Development variables
    └── prod/
        └── terraform.tfvars    # Production variables
```

## Module Examples

### 1. S3 Buckets Module

**File**: `modules/s3-buckets/main.tf`

```hcl
variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "enable_versioning" {
  description = "Enable bucket versioning"
  type        = bool
  default     = true
}

# Data Lake Bucket
resource "aws_s3_bucket" "datalake" {
  bucket = "openagdb-datalake-${var.environment}-${var.region}"

  tags = {
    Name        = "OpenAgDB Data Lake"
    Environment = var.environment
    Project     = "OpenAgDB"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  rule {
    id     = "transition-old-versions"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }
}

# Artifacts Bucket
resource "aws_s3_bucket" "artifacts" {
  bucket = "openagdb-artifacts-${var.environment}-${var.region}"

  tags = {
    Name        = "OpenAgDB Artifacts"
    Environment = var.environment
    Project     = "OpenAgDB"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    id     = "delete-old-artifacts"
    status = "Enabled"

    expiration {
      days = 30
    }
  }
}

# Bucket Policies
resource "aws_s3_bucket_policy" "datalake" {
  bucket = aws_s3_bucket.datalake.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyInsecureTransport"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.datalake.arn,
          "${aws_s3_bucket.datalake.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      {
        Sid    = "DenyUnencryptedObjectUploads"
        Effect = "Deny"
        Principal = "*"
        Action = "s3:PutObject"
        Resource = "${aws_s3_bucket.datalake.arn}/*"
        Condition = {
          StringNotEquals = {
            "s3:x-amz-server-side-encryption" = "AES256"
          }
        }
      }
    ]
  })
}

output "datalake_bucket_name" {
  description = "Data lake bucket name"
  value       = aws_s3_bucket.datalake.id
}

output "datalake_bucket_arn" {
  description = "Data lake bucket ARN"
  value       = aws_s3_bucket.datalake.arn
}

output "artifacts_bucket_name" {
  description = "Artifacts bucket name"
  value       = aws_s3_bucket.artifacts.id
}

output "artifacts_bucket_arn" {
  description = "Artifacts bucket ARN"
  value       = aws_s3_bucket.artifacts.arn
}
```

### 2. IAM OIDC Provider Module

**File**: `modules/iam-oidc/main.tf`

```hcl
variable "github_org" {
  description = "GitHub organization or user"
  type        = string
  default     = "adam133"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "equipment-testing"
}

data "tls_certificate" "github_actions" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github_actions" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github_actions.certificates[0].sha1_fingerprint]

  tags = {
    Name      = "GitHub Actions OIDC Provider"
    Project   = "OpenAgDB"
    ManagedBy = "Terraform"
  }
}

output "oidc_provider_arn" {
  description = "ARN of the GitHub Actions OIDC provider"
  value       = aws_iam_openid_connect_provider.github_actions.arn
}
```

### 3. IAM Roles Module

**File**: `modules/iam-roles/main.tf`

```hcl
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "oidc_provider_arn" {
  description = "ARN of GitHub OIDC provider"
  type        = string
}

variable "datalake_bucket_arn" {
  description = "ARN of data lake bucket"
  type        = string
}

variable "artifacts_bucket_arn" {
  description = "ARN of artifacts bucket"
  type        = string
}

variable "github_org" {
  description = "GitHub organization"
  type        = string
  default     = "adam133"
}

variable "github_repo" {
  description = "GitHub repository"
  type        = string
  default     = "equipment-testing"
}

data "aws_caller_identity" "current" {}

# GitHub Actions Deployment Role
resource "aws_iam_role" "github_actions" {
  name        = "GitHubActionsDeploymentRole-OpenAgDB-${var.environment}"
  # Note: The role name includes the environment suffix (e.g., "GitHubActionsDeploymentRole-OpenAgDB-prod")
  # This differs from AWS_CONFIGURATION.md which shows a generic name without the suffix
  description = "Role for GitHub Actions to deploy OpenAgDB infrastructure"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "GitHub Actions Deployment Role"
    Environment = var.environment
    Project     = "OpenAgDB"
    ManagedBy   = "Terraform"
  }
}

# Scraper Role
resource "aws_iam_role" "scraper" {
  name        = "OpenAgDB-ScraperRole-${var.environment}"
  description = "Role for scrapers to write data to S3"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "Scraper Execution Role"
    Environment = var.environment
    Project     = "OpenAgDB"
    ManagedBy   = "Terraform"
  }
}

# API Lambda Role
resource "aws_iam_role" "api_lambda" {
  name        = "OpenAgDB-APIRole-${var.environment}"
  description = "Role for API Lambda to read from S3"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "API Lambda Role"
    Environment = var.environment
    Project     = "OpenAgDB"
    ManagedBy   = "Terraform"
  }
}

# Scraper Policy
resource "aws_iam_role_policy" "scraper" {
  name = "OpenAgDB-ScraperPolicy"
  role = aws_iam_role.scraper.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "WriteToDataLake"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.datalake_bucket_arn,
          "${var.datalake_bucket_arn}/*"
        ]
      },
      {
        Sid    = "WriteArtifacts"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          "${var.artifacts_bucket_arn}/*"
        ]
      }
    ]
  })
}

# API Lambda Policy
resource "aws_iam_role_policy" "api_lambda" {
  name = "OpenAgDB-APIPolicy"
  role = aws_iam_role.api_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ReadDataLake"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.datalake_bucket_arn,
          "${var.datalake_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Attach AWS managed policy for Lambda basic execution
resource "aws_iam_role_policy_attachment" "api_lambda_basic" {
  role       = aws_iam_role.api_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Deployment Policy for GitHub Actions
resource "aws_iam_role_policy" "github_actions_deployment" {
  name = "OpenAgDB-DeploymentPolicy"
  role = aws_iam_role.github_actions.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3Access"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = [
          var.datalake_bucket_arn,
          "${var.datalake_bucket_arn}/*",
          var.artifacts_bucket_arn,
          "${var.artifacts_bucket_arn}/*"
        ]
      },
      {
        Sid    = "LambdaDeployment"
        Effect = "Allow"
        Action = [
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:PublishVersion",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration"
        ]
        Resource = "arn:aws:lambda:*:${data.aws_caller_identity.current.account_id}:function:openagdb-*"
      }
    ]
  })
}

output "github_actions_role_arn" {
  description = "ARN of GitHub Actions deployment role"
  value       = aws_iam_role.github_actions.arn
}

output "scraper_role_arn" {
  description = "ARN of scraper role"
  value       = aws_iam_role.scraper.arn
}

output "api_lambda_role_arn" {
  description = "ARN of API Lambda role"
  value       = aws_iam_role.api_lambda.arn
}
```

### 4. Root Module

**File**: `main.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    # Note: Customize these values for your environment
    # For multiple environments, use unique bucket names or workspace-specific keys
    # Example: key = "${terraform.workspace}/infrastructure/terraform.tfstate"
    bucket         = "openagdb-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "openagdb-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "OpenAgDB"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

module "iam_oidc" {
  source = "./modules/iam-oidc"

  github_org  = var.github_org
  github_repo = var.github_repo
}

module "s3_buckets" {
  source = "./modules/s3-buckets"

  environment        = var.environment
  region             = var.aws_region
  enable_versioning  = var.enable_versioning
}

module "iam_roles" {
  source = "./modules/iam-roles"

  environment          = var.environment
  oidc_provider_arn    = module.iam_oidc.oidc_provider_arn
  datalake_bucket_arn  = module.s3_buckets.datalake_bucket_arn
  artifacts_bucket_arn = module.s3_buckets.artifacts_bucket_arn
  github_org           = var.github_org
  github_repo          = var.github_repo
}
```

**File**: `variables.tf`

```hcl
variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod'."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "github_org" {
  description = "GitHub organization or user"
  type        = string
  default     = "adam133"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "equipment-testing"
}

variable "enable_versioning" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}
```

**File**: `outputs.tf`

```hcl
output "datalake_bucket" {
  description = "Data lake S3 bucket name"
  value       = module.s3_buckets.datalake_bucket_name
}

output "artifacts_bucket" {
  description = "Artifacts S3 bucket name"
  value       = module.s3_buckets.artifacts_bucket_name
}

output "github_actions_role_arn" {
  description = "ARN for GitHub Actions deployment role"
  value       = module.iam_roles.github_actions_role_arn
}

output "scraper_role_arn" {
  description = "ARN for scraper execution role"
  value       = module.iam_roles.scraper_role_arn
}

output "api_lambda_role_arn" {
  description = "ARN for API Lambda execution role"
  value       = module.iam_roles.api_lambda_role_arn
}
```

**File**: `versions.tf`

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
}
```

### 5. Environment-Specific Variables

**File**: `environments/prod/terraform.tfvars`

```hcl
environment        = "prod"
aws_region         = "us-east-1"
github_org         = "adam133"
github_repo        = "equipment-testing"
enable_versioning  = true
```

**File**: `environments/dev/terraform.tfvars`

```hcl
environment        = "dev"
aws_region         = "us-east-1"
github_org         = "adam133"
github_repo        = "equipment-testing"
enable_versioning  = false
```

## Usage Instructions

### 1. Initialize Backend

First, create the S3 bucket and DynamoDB table for Terraform state:

```bash
# Create state bucket
aws s3 mb s3://openagdb-terraform-state --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket openagdb-terraform-state \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name openagdb-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# Enable point-in-time recovery (PITR) for the lock table
aws dynamodb update-continuous-backups \
  --table-name openagdb-terraform-locks \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
  --region us-east-1
```

### 2. Deploy Infrastructure

```bash
# Production
terraform init
terraform plan -var-file="environments/prod/terraform.tfvars"
terraform apply -var-file="environments/prod/terraform.tfvars"

# Development
# Note: When using workspaces, consider using workspace-specific state keys in the backend configuration
# to avoid state conflicts. See backend configuration comments above.
terraform workspace new dev
terraform plan -var-file="environments/dev/terraform.tfvars"
terraform apply -var-file="environments/dev/terraform.tfvars"
```

### 3. Get Outputs

```bash
# Get role ARN for GitHub secrets
terraform output github_actions_role_arn

# Get bucket names
terraform output datalake_bucket
terraform output artifacts_bucket
```

### 4. Update GitHub Secrets

Use the Terraform outputs to configure GitHub secrets:

```bash
gh secret set AWS_DEPLOYMENT_ROLE_ARN --body "$(terraform output -raw github_actions_role_arn)"
gh secret set S3_DATALAKE_BUCKET --body "$(terraform output -raw datalake_bucket)"
gh secret set S3_ARTIFACTS_BUCKET --body "$(terraform output -raw artifacts_bucket)"
gh secret set AWS_REGION --body "us-east-1"
gh secret set AWS_ACCOUNT_ID --body "$(aws sts get-caller-identity --query Account --output text)"
```

## Cleanup

To destroy all infrastructure:

```bash
terraform destroy -var-file="environments/prod/terraform.tfvars"
```

## Best Practices

1. **State Management**: Always use remote state with locking
2. **Workspaces**: Use separate workspaces for dev/prod
3. **Variables**: Never commit `.tfvars` files with secrets
4. **Modules**: Keep modules reusable and well-documented
5. **Validation**: Use variable validation for input constraints
6. **Tagging**: Apply consistent tags for resource management
7. **Outputs**: Export values needed by other systems

## Troubleshooting

### Issue: OIDC provider already exists

If the provider already exists, import it:

```bash
terraform import module.iam_oidc.aws_iam_openid_connect_provider.github_actions \
  arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com
```

### Issue: Bucket name already taken

S3 bucket names are globally unique. Update the naming pattern in the variables.

### Issue: Permission denied

Ensure your AWS credentials have permission to create IAM roles and S3 buckets.

## Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS S3 Terraform Module](https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/latest)
