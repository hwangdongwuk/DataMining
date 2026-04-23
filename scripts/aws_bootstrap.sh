#!/usr/bin/env bash
# S3 버킷 생성 + raw 데이터 업로드 자동화
# 전제: `aws configure` 완료, IAM에 S3FullAccess 권한 있음

set -euo pipefail

REGION="${AWS_REGION:-ap-southeast-2}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET="${S3_BUCKET:-datamining-${ACCOUNT_ID}-raw}"

echo "[1/4] 계정 확인: ${ACCOUNT_ID} / 리전: ${REGION} / 버킷: ${BUCKET}"

echo "[2/4] 버킷 존재 확인"
if aws s3api head-bucket --bucket "${BUCKET}" 2>/dev/null; then
  echo "  → 이미 존재"
else
  echo "  → 생성"
  aws s3api create-bucket \
    --bucket "${BUCKET}" \
    --region "${REGION}" \
    --create-bucket-configuration LocationConstraint="${REGION}"
  aws s3api put-public-access-block --bucket "${BUCKET}" \
    --public-access-block-configuration \
      "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
  aws s3api put-bucket-versioning --bucket "${BUCKET}" \
    --versioning-configuration Status=Enabled
fi

echo "[3/4] raw JSONL 업로드 → s3://${BUCKET}/raw/narajangteo/"
aws s3 sync data/raw/narajangteo/ \
  "s3://${BUCKET}/raw/narajangteo/" \
  --exclude "*" --include "*.jsonl" \
  --only-show-errors
echo "  done"

echo "[4/4] 가공 데이터 업로드 → s3://${BUCKET}/processed/"
if [ -d data/processed ] && [ "$(ls -A data/processed)" ]; then
  aws s3 sync data/processed/ \
    "s3://${BUCKET}/processed/" \
    --only-show-errors
  echo "  done"
else
  echo "  → data/processed 비어있음. 전처리 후 재실행."
fi

echo ""
echo "✓ 완료. 확인:"
echo "  aws s3 ls s3://${BUCKET}/ --recursive --summarize | tail"
