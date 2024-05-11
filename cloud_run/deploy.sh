#!/bin/bash

PROJECT_ID="loyal-theater-415906"
IMAGE_NAME="cv_analyzer_image_v13"
SERVICE_NAME="cvanalyzer"
OPEN_AI_TOKEN_SECRET_NAME="open_ai_token:latest"
OPEN_AI_TOKEN_ENV_VAR_NAME="OPEN_AI_TOKEN"
DATASET_NAME_VALUE="datasets_nulp"
DATASET_NAME_ENV_VAR_NAME="DATASET_NAME"

docker build -t $IMAGE_NAME cv_analyzer --platform linux/amd64

docker tag $IMAGE_NAME gcr.io/$PROJECT_ID/$IMAGE_NAME
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME

gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
  --platform managed \
  --memory=1024Mi \
  --update-env-vars=$DATASET_NAME_ENV_VAR_NAME=$DATASET_NAME_VALUE \
  --update-secrets=$OPEN_AI_TOKEN_ENV_VAR_NAME=$OPEN_AI_TOKEN_SECRET_NAME \
  --region europe-west1


