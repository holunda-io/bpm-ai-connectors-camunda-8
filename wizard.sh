#!/bin/bash

# URL of the element templates
templates_url="https://raw.githubusercontent.com/holunda-io/bpm-ai-connectors-camunda-8/main/bpmn/.camunda/element-templates"
# List of element template files to download
templates=(
    "bpm-ai-connector-compose.json"
    "bpm-ai-connector-decide.json"
    "bpm-ai-connector-extract.json"
    "bpm-ai-connector-generic.json"
    "bpm-ai-connector-translate.json"
)

##############################################################################################################################
# Download docker-compose.yml, create .env file and ./bpm-ai/data directory to mount into the container
##############################################################################################################################

echo "[bpm.ai Wizard]"

mkdir -p bpm-ai/data bpm-ai/.cache && cd bpm-ai || exit

# download docker-compose.yml
curl -sSL https://raw.githubusercontent.com/holunda-io/bpm-ai-connectors-camunda-8/main/docker-compose.yml -o docker-compose.yml

# create .env file if it doesn't exist
touch .env

# Determine cluster_type based on existing .env settings
if grep -q "ZEEBE_CLIENT_CLOUD_CLUSTER-ID" .env; then
  cluster_type="cloud"
elif grep -q "ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS" .env; then
  cluster_type="local"
else
  cluster_type=""
fi

# Ask for cluster_type if not determined by .env
if [ -z "$cluster_type" ]; then
  read -rp "Use Camunda Cloud or local cluster (started automatically)? [cloud/local] (default: local): " input_cluster_type
  cluster_type=${input_cluster_type:-local}
fi

echo "Using cluster type: $cluster_type"

if [ "$cluster_type" = "cloud" ]; then
  if ! grep -q "ZEEBE_CLIENT_CLOUD_CLUSTER-ID" .env; then
    read -rp "Zeebe Cloud Cluster ID: " x && echo "ZEEBE_CLIENT_CLOUD_CLUSTER-ID=$x" >> .env
  fi

  if ! grep -q "ZEEBE_CLIENT_CLOUD_CLIENT-ID" .env; then
    read -rp "Zeebe Cloud Client ID: " x && echo "ZEEBE_CLIENT_CLOUD_CLIENT-ID=$x" >> .env
  fi

  if ! grep -q "ZEEBE_CLIENT_CLOUD_CLIENT-SECRET" .env; then
    read -s -rp "Zeebe Cloud Client Secret: " x && echo "ZEEBE_CLIENT_CLOUD_CLIENT-SECRET=$x" >> .env
    echo ""
  fi
elif [ "$cluster_type" = "local" ]; then
  if ! grep -q "ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS" .env; then
    echo "ZEEBE_CLIENT_BROKER_GATEWAY-ADDRESS=zeebe:26500" >> .env
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

read -rp "Enable local AI models for decide/extract/translate and OCR (larger download)? [y/n] (default: n): " inference
# Set 'n' as the default choice if the user just hits enter
inference=${inference:-n}

if [ "$inference" = "y" ]; then
  profile_flags="$profile_flags --profile inference"
fi

##############################################################################################################################
# Determine OS, try to find Camunda Modeler installation, and download and install element templates
##############################################################################################################################

unameOut=$(uname -a)
case "${unameOut}" in
    *Microsoft*)     OS="Windows";; #wls must be first since it will have Linux in the name too
    *microsoft*)     OS="Windows";; 
    Linux*)     OS="Linux";;
    Darwin*)    OS="macOS";;
    *)          OS="UNKNOWN:${unameOut}"
esac

echo "Detected $OS."

# Define an array of path patterns
declare -a path_patterns_mac=(
    "/Applications/Camunda Modeler.app"
    "/Applications/*/Camunda Modeler.app"
    "/Users/*/Downloads/Camunda Modeler.app"
    "/Users/*/Downloads/*/Camunda Modeler.app"
)

declare -a path_patterns_windows=(
    "/mnt/c/Program Files/Camunda Modeler.exe"
    "/mnt/c/Program Files (x86)/Camunda Modeler.exe"
    "/mnt/c/Program Files/*/Camunda Modeler.exe"
    "/mnt/c/Program Files (x86)/*/Camunda Modeler.exe"
    "/mnt/c/Users/*/Downloads/Camunda Modeler.exe"
    "/mnt/c/Users/*/Downloads/*/Camunda Modeler.exe"
)

declare -a path_patterns_linux=(
    "/usr/bin/camunda-modeler"
    # todo
)

# Select the correct array of path patterns based on the detected OS
case "$OS" in
    "macOS") path_patterns=("${path_patterns_mac[@]}");;
    "Windows") path_patterns=("${path_patterns_windows[@]}");;
    "Linux") path_patterns=("${path_patterns_linux[@]}");;
    *) echo "Unsupported OS for this script"; exit 1;;
esac

# Function to count slashes in a path
count_slashes() {
    echo "$1" | awk -F"/" '{print NF-1}'
}

# Function to extract the base directory from a pattern
extract_base_dir() {
    local pattern="$1"
    # Extract everything up to the first wildcard "*"
    local base_dir="${pattern%%\**}"
    # If the result ends with a slash, remove it, unless it's just the root "/"
    if [[ "${base_dir}" != "/" ]]; then
        base_dir="${base_dir%%/}"
    fi
    # Ensure we return the base directory up to the first directory level without wildcards
    echo "$base_dir"
}

echo "Searching for Camunda Modeler installation..."

# Initialize an array to collect found paths
declare -a paths_array=()

# Iterate over each path pattern
for pattern in "${path_patterns[@]}"; do
    # Determine the base directory for the find command by extracting the part before the first wildcard
    base_dir=$(extract_base_dir "$pattern")

    # Calculate maxdepth based on the number of slashes in the pattern
    # Subtract the number of slashes in base_dir from the total in pattern
    total_slashes=$(count_slashes "$pattern")
    base_dir_slashes=$(count_slashes "$base_dir")
    maxdepth=$((total_slashes - base_dir_slashes + 1))

    # Use find to search for the pattern
    #find "$base_dir" -path "$pattern" -maxdepth "$maxdepth" -print 2>/dev/null

    # Use find to search for the pattern and collect found paths
    while IFS= read -r line; do
        paths_array+=("$line")
    done < <(find "$base_dir" -path "$pattern" -maxdepth "$maxdepth" -print 2>/dev/null)
done

# Check the number of found paths
num_paths=${#paths_array[@]}
modeler_path=""

if [ "$num_paths" -eq 0 ]; then
    echo "No Camunda Modeler installations found. Please install element templates manually: https://github.com/holunda-io/bpm-ai-connectors-camunda-8/tree/main?tab=readme-ov-file#-use-element-templates-in-your-processes"
elif [ "$num_paths" -eq 1 ]; then
    modeler_path="${paths_array[0]}"
    echo "Found Camunda Modeler: $modeler_path"
else
    echo "Multiple Modeler installations found. Please select one:"
    for i in "${!paths_array[@]}"; do
        echo "$((i+1))) ${paths_array[$i]}"
    done
    read -p "Enter number (1-$num_paths): " selection
    if [[ $selection =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le $num_paths ]; then
        modeler_path="${paths_array[$((selection-1))]}"
        echo "You selected: $modeler_path"
    else
        echo "Invalid selection. Exiting."
        exit 1
    fi
fi

# Determine the target directory for the element templates
if [[ $OS == "macOS" ]]; then
    templates_target="$modeler_path/Contents/MacOS/resources/element-templates"
else
    templates_target="$(dirname "$modeler_path")/resources/element-templates"
fi

echo "Installing element templates into $templates_target..."

# Ensure the target directory exists
mkdir -p "$templates_target"

# Download each template
for template in "${templates[@]}"; do
    curl -sSL "$templates_url/$template" -o "$templates_target/$template"
done

##############################################################################################################################
# Start docker compose with selected profile(s)
##############################################################################################################################

eval "docker compose$profile_flags up -d"
