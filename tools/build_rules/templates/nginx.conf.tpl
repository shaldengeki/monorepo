server {
    listen 80 default_server;
    server_name {server_name};
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
