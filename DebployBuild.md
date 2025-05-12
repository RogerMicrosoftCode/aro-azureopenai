

* First, set your environment variables with the plain text values in your terminal:

COPI URL ENDPOINT IA AND COPY TOCKEN OPENIA ON TXT AND UPDATE IN THE NEXT VARIABLES
```md
export OPENAI_API_BASE="https://MY_FANCY_URL.openai.azure.com/"
export OPENAI_API_KEY="your-api-key"
export NAMESPACE="aro-azureopenai"
export PROJECT="aro-azureopenai"
```

```md
OC TOKEN CONSOLE AZURE REDHAT OPENSHIFT
oc project $PROJECT
kubectl apply -k manifests/overlays/ocp
```

* Deploy the secret in the namespace

```md
cat <<EOF | kubectl apply -n $NAMESPACE -f -
apiVersion: v1
kind: Secret
metadata:
  name: azure-openai
type: Opaque
data:
  OPENAI_API_BASE: $(echo -n "$OPENAI_API_BASE" | base64)
  OPENAI_API_KEY: $(echo -n "$OPENAI_API_KEY" | base64)
EOF
```