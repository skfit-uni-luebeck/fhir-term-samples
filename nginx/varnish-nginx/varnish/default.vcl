vcl 4.0;

backend default {
  .host = "nginx:80";
}

sub vcl_backend_response {
//set the cache TTL to one hour unconditionally.
    set beresp.ttl = 1h;
}
