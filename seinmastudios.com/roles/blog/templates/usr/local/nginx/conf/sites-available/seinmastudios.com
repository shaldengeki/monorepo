server {
  listen [::]:80;
  listen 80;

  # listen on both hosts
  server_name {{app_host}} www.{{app_host}};

  # and redirect to the https host (declared below)
  # avoiding http://www -> https://www -> https:// chain.
  return 301 https://{{app_host}}$request_uri;
}

server {
  listen [::]:443 ssl http2;
  listen 443 ssl http2;

  # listen on the wrong host
  server_name www.{{app_host}};

  include h5bp/directive-only/ssl.conf;

  ssl_certificate {{app_dir}}/ssl/live/{{app_host}}/fullchain.pem;
  ssl_certificate_key {{app_dir}}/ssl/live/{{app_host}}/privkey.pem;

  # and redirect to the non-www host (declared below)
  return 301 https://{{app_host}}$request_uri;
}

server {
  listen [::]:443 ssl http2;
  listen 443 ssl http2;

  # The host name to respond to
  server_name {{app_host}};

  include h5bp/directive-only/ssl.conf;

  ssl_certificate {{app_dir}}/ssl/live/{{app_host}}/fullchain.pem;
  ssl_certificate_key {{app_dir}}/ssl/live/{{app_host}}/privkey.pem;

  # Path for static files
  root {{app_dir}}/public;

  #Specify a charset
  charset utf-8;

  # Custom 404 page
  error_page 404 /404.html;

  # Include the basic h5bp config set
  include h5bp/basic.conf;

  access_log {{app_dir}}/logs/access.log;
  error_log {{app_dir}}/logs/error.log;

  location / {
    index index.html;
  }
}
