ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM $BUILD_FROM
# Čistý Python bez závislostí (http.server + urllib)
RUN apk add --no-cache python3 bash jq ca-certificates
COPY proxy.py run.sh /app/
RUN chmod +x /app/run.sh
CMD ["/app/run.sh"]
