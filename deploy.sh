#!/usr/bin/env bash
#
# Deploys this Azure Function App to "AttendanceReportApp".
#
# Prerequisites:
#   - Azure CLI (az) and Azure Functions Core Tools (func) installed
#   - Run `az login` before running this script
#
set -euo pipefail

FUNCTION_APP_NAME="AttendanceReportApp"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v az >/dev/null 2>&1; then
    echo "Error: Azure CLI (az) is not installed. See https://learn.microsoft.com/cli/azure/install-azure-cli" >&2
    exit 1
fi

if ! command -v func >/dev/null 2>&1; then
    echo "Error: Azure Functions Core Tools (func) is not installed. See https://learn.microsoft.com/azure/azure-functions/functions-run-local" >&2
    exit 1
fi

if ! az account show >/dev/null 2>&1; then
    echo "Error: You are not logged in to Azure. Run 'az login' first." >&2
    exit 1
fi

echo "Deploying to Azure Function App '$FUNCTION_APP_NAME'..."
func azure functionapp publish "$FUNCTION_APP_NAME" --python

echo "Deployment complete."
