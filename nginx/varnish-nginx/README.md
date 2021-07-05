# Transparent Ontoserver Authentication with Caching

## Files in this directory

## varnish/Dockerfile

Build a varnish image with the provided `default.vcl` configuration file

## varnish/default.vcl

Settings for varnish caching proxy. Upstream will not need to be changed in this setup, it points to nginx. The caching TTL should be tuned to ensure that changes in the upstream propagate quickly. You can also configure varnish to refresh (stale) keys in the background. Refer to varnish documentation on how to do that.

## nginx

You will need the following key material:

- chain.pem: The full chain of the remote endpoint. The chain for terminology-highmed.medic.medfak.uni-koeln.de is provided in this repository.
- cert-with-chain.pem: The OpenSSL PEM format public key with chain of your DFN-issued certificate
- private.pem: The associcated private key in OpenSSL PEM format

### nginx.conf

The provided configuration terminates SSL for the following routes:

- /au -> https://r4.ontoserver.csiro.au/
- /koeln -> https://terminology-highmed.medic.medfak.uni-koeln.de/

/au requires no authentication.

For /koeln, the provided key material is used to authenticate towards the server. Nginx terminates the SSL connection and exposes the upstream over HTTP on port 80. Varnish is generally not used to terminate SSL, so that nginx fills in that role.

## Building

```bash
docker-compose up --build
```

after copying the required key material for nginx.

By default, varnish is exposed over HTTP on Port 80 (http://localhost/koeln/fhir/metadata)
