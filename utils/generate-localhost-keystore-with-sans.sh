#!/bin/bash
set -e

# === Configuration ===
CA_KEY="rootCA.key"
CA_CERT="rootCA.crt"
CA_SUBJ="/C=US/ST=Local/L=Local/O=MyRootCA/CN=MyRootCA"

LOCAL_KEY="localhost.key"
LOCAL_CSR="localhost.csr"
LOCAL_CERT="localhost.crt"
LOCAL_P12="localhost.pkcs12"
LOCAL_SUBJ="/C=US/ST=Local/L=Local/O=LocalDev/CN=localhost"

DAYS=825
PASSWORD="changeit"
ALIAS="localhost"

echo "=== Step 1: Generate Root CA ==="
openssl genrsa -out "$CA_KEY" 4096
openssl req -x509 -new -nodes -key "$CA_KEY" -sha256 -days "$DAYS" -subj "$CA_SUBJ" -out "$CA_CERT"

echo "=== Step 2: Generate localhost key and CSR ==="
openssl genrsa -out "$LOCAL_KEY" 2048
openssl req -new -key "$LOCAL_KEY" -subj "$LOCAL_SUBJ" -out "$LOCAL_CSR"

echo "=== Step 3: Create localhost certificate signed by CA with SANs ==="
cat > localhost.ext <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = kafka1
DNS.3 = kafka2
DNS.4 = kafka3
DNS.5 = kafka4
IP.1 = 127.0.0.1
EOF

openssl x509 -req -in "$LOCAL_CSR" -CA "$CA_CERT" -CAkey "$CA_KEY" -CAcreateserial \
  -out "$LOCAL_CERT" -days "$DAYS" -sha256 -extfile localhost.ext

echo "=== Step 4: Export to PKCS#12 (.p12) with alias '$ALIAS' and password '$PASSWORD' ==="
openssl pkcs12 -export \
  -name "$ALIAS" \
  -out "$LOCAL_P12" \
  -inkey "$LOCAL_KEY" \
  -in "$LOCAL_CERT" \
  -certfile "$CA_CERT" \
  -password pass:"$PASSWORD"

echo "=== Step 5: Export CA certificate as ca.crt ==="
cp "$CA_CERT" ca.crt

echo
echo "Created PKCS#12 keystore: $LOCAL_P12"
echo "Password: $PASSWORD"
echo "Alias: $ALIAS"
echo
echo "SAN entries included:"
echo "  - localhost"
echo "  - kafka1"
echo "  - kafka2"
echo "  - kafka3"
echo "  - kafka4"
echo "  - 127.0.0.1"