FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY gateway/nginx.conf /etc/nginx/nginx.conf
COPY gateway/docs/ /usr/share/nginx/html/docs/

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD wget -qO- http://127.0.0.1:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
