#!/usr/bin/env bash
# EC2에 DataMining 레포 배포 + Streamlit 백그라운드 실행.
# 사전: SSH 키 ~/.ssh/datamining/datademo.pem, SG 8501 포트 허용.

set -euo pipefail

EC2_USER="ec2-user"
EC2_HOST="13.239.237.95"
KEY="$HOME/.ssh/datamining/datademo.pem"
REPO_URL="https://github.com/hwangdongwuk/DataMining.git"
BUCKET="datamining-257925264162-raw"

SSH="ssh -i $KEY -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST"

echo "[1/6] EC2 환경 설치 (git, python, pip)"
$SSH <<'REMOTE'
set -e
sudo dnf install -y git python3 python3-pip >/dev/null 2>&1 || true
python3 --version
REMOTE

echo "[2/6] 레포 clone / pull"
$SSH <<REMOTE
set -e
if [ -d ~/DataMining/.git ]; then
  cd ~/DataMining && git pull --rebase origin main
else
  git clone $REPO_URL ~/DataMining
fi
REMOTE

echo "[3/6] venv + 패키지 설치"
$SSH <<'REMOTE'
set -e
cd ~/DataMining
python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet streamlit pandas plotly python-dotenv numpy
echo "  installed"
REMOTE

echo "[4/6] processed CSV 다운로드 from S3"
$SSH <<REMOTE
set -e
cd ~/DataMining
mkdir -p data/processed
aws s3 sync s3://$BUCKET/processed/ data/processed/ \
  --exclude "*" --include "*.csv" --only-show-errors || \
  echo "  (S3 접근 실패는 무시 — 로컬에서 scp로 전송 필요)"
ls -la data/processed/
REMOTE

echo "[5/6] 기존 Streamlit 프로세스 종료"
$SSH "pkill -f streamlit || true"

echo "[6/6] Streamlit nohup 기동 (8501)"
$SSH <<'REMOTE'
cd ~/DataMining
nohup .venv/bin/streamlit run src/app_streamlit.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --browser.gatherUsageStats false \
  >/tmp/streamlit.log 2>&1 &
sleep 3
ps -ef | grep streamlit | grep -v grep | head -3
echo "---"
curl -s http://localhost:8501/_stcore/health || echo "health not yet ready"
REMOTE

echo ""
echo "✓ 배포 완료. 접속:"
echo "  http://$EC2_HOST:8501"
