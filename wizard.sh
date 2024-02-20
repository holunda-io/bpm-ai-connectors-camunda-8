#!/bin/sh
echo "[bpm.ai Wizard]"

mkdir -p bpm-ai/data && cd bpm-ai || exit

# download docker-compose.yml
curl -sSL https://raw.githubusercontent.com/holunda-io/bpm-ai-connectors-camunda-8/bpm-ai/docker-compose.yml -o docker-compose.yml

# create .env file if it doesn't exist
touch .env

# Initialize profile flags
profile_flags=""

read -rp "Use Camunda Cloud or local cluster (started automatically)? [cloud/local] (default: local): " cluster_type
# Set 'local' as the default choice if the user just hits enter
cluster_type=${cluster_type:-local}

if [ "$cluster_type" = "cloud" ]; then
  if ! grep -q "ZEEBE_CLIENT_CLOUD_CLUSTER-ID" .env; then
    read -rp "ZEEBE_CLIENT_CLOUD_CLUSTER-ID: " x && echo "ZEEBE_CLIENT_CLOUD_CLUSTER-ID=$x" >> .env
  fi

  if ! grep -q "ZEEBE_CLIENT_CLOUD_CLIENT-ID" .env; then
    read -rp "ZEEBE_CLIENT_CLOUD_CLIENT-ID: " x && echo "ZEEBE_CLIENT_CLOUD_CLIENT-ID=$x" >> .env
  fi

  if ! grep -q "ZEEBE_CLIENT_CLOUD_CLIENT-SECRET" .env; then
    read -rp "ZEEBE_CLIENT_CLOUD_CLIENT-SECRET: " x && echo "ZEEBE_CLIENT_CLOUD_CLIENT-SECRET=$x" >> .env
  fi
elif [ "$cluster_type" = "local" ]; then
  if ! grep -q "ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS" .env; then
    echo "ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=localhost:26500" >> .env
  fi
else
  echo "Unknown option ${cluster_type}"
  exit
fi

if ! grep -q "OPENAI_API_KEY" .env; then
  read -rp "OpenAI API Key (leave blank if not needed): " x && echo "OPENAI_API_KEY=$x" >> .env
fi

if [ "$cluster_type" = "local" ]; then
  profile_flags="$profile_flags --profile platform"
fi

read -rp "Enable local, non-LLM AI models for decision/extraction/translation (up to 2GB addtional download and higher RAM requirement)? [y/n] (default: n): " inference
# Set 'n' as the default choice if the user just hits enter
inference=${inference:-n}

if [ "$inference" = "y" ]; then
  profile_flags="$profile_flags --profile inference"
else
  profile_flags="$profile_flags --profile default"
fi

eval "docker compose$profile_flags up -d"
