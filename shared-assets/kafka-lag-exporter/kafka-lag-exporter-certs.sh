#!/bin/bash

CA_PATH=$1

i=$2

# Create host keystore
keytool -genkey -noprompt \
			 -alias $i \
			 -dname "CN=$i,OU=TEST,O=CONFLUENT,L=PaloAlto,S=Ca,C=US" \
                         -ext "SAN=dns:$i,dns:localhost" \
			 -keystore kafka.$i.keystore.jks \
			 -keyalg RSA \
			 -storepass confluent \
			 -keypass confluent \
       -storetype JKS

# Create the certificate signing request (CSR)
keytool -keystore kafka.$i.keystore.jks -alias $i -certreq -file $i.csr -storepass confluent -keypass confluent -ext "SAN=dns:$i,dns:localhost"
#openssl req -in $i.csr -text -noout

# Enables 'confluent login --ca-cert-path /etc/kafka/secrets/snakeoil-ca-1.crt --url https://kafka1:8091'
DNS_ALT_NAMES=$(printf '%s\n' "DNS.1 = $i" "DNS.2 = localhost")
if [[ "$i" == "mds" ]]; then
  DNS_ALT_NAMES=$(printf '%s\n' "$DNS_ALT_NAMES" "DNS.3 = kafka1" "DNS.4 = kafka2")
fi
# control-center and ksqldb-server share a certificate
if [[ "$i" == "controlCenterAndKsqlDBServer" ]]; then
  DNS_ALT_NAMES=$(printf '%s\n' "$DNS_ALT_NAMES" "DNS.3 = control-center" "DNS.4 = ksqldb-server")
fi

# Sign the host certificate with the certificate authority (CA)
# Set a random serial number (avoid problems from using '-CAcreateserial' when parallelizing certificate generation)
CERT_SERIAL=$(awk -v seed="$RANDOM" 'BEGIN { srand(seed); printf("0x%.4x%.4x%.4x%.4x\n", rand()*65535 + 1, rand()*65535 + 1, rand()*65535 + 1, rand()*65535 + 1) }')
openssl x509 -req -CA ${CA_PATH}/snakeoil-ca-1.crt -CAkey ${CA_PATH}/snakeoil-ca-1.key -in $i.csr -out $i-ca1-signed.crt -sha256 -days 365 -set_serial ${CERT_SERIAL} -passin pass:confluent -extensions v3_req -extfile <(cat <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
CN = $i
[v3_req]
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names
[alt_names]
$DNS_ALT_NAMES
EOF
)
#openssl x509 -noout -text -in $i-ca1-signed.crt

# Sign and import the CA cert into the keystore
keytool -noprompt -keystore kafka.$i.keystore.jks -alias snakeoil-caroot -import -file ${CA_PATH}/snakeoil-ca-1.crt -storepass confluent -keypass confluent
#keytool -list -v -keystore kafka.$i.keystore.jks -storepass confluent

# Sign and import the host certificate into the keystore
keytool -noprompt -keystore kafka.$i.keystore.jks -alias $i -import -file $i-ca1-signed.crt -storepass confluent -keypass confluent -ext "SAN=dns:$i,dns:localhost"
#keytool -list -v -keystore kafka.$i.keystore.jks -storepass confluent

# Create truststore and import the CA cert
keytool -noprompt -keystore kafka.$i.truststore.jks -storetype JKS -alias snakeoil-caroot -import -file ${CA_PATH}/snakeoil-ca-1.crt -storepass confluent -keypass confluent

# Save creds
echo "confluent" > ${i}_sslkey_creds
echo "confluent" > ${i}_keystore_creds
echo "confluent" > ${i}_truststore_creds
