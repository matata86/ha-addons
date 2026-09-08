ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM
# Luna je staticky slinkovaná (UPX) Go binárka – stačí bash, jq, curl a certifikáty.
# Samotná binárka se do image nekopíruje (není volně šiřitelná): addon ji při startu
# vezme z /share/luna/luna, nebo stáhne z adresy v nastavení, a uloží do /data.
RUN apk add --no-cache bash jq curl ca-certificates tzdata
COPY run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]
