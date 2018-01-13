FROM nginx:alpine
RUN rm /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/nginx.conf
ADD conf/conf.d/*  /etc/nginx/conf.d
ADD conf/nginx.conf /etc/nginx/nginx.conf 
RUN mkdir -p /www/static
RUN sleep 7