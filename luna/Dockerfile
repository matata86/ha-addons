ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-debian:latest
FROM $BUILD_FROM
# Debian base (ne Alpine): od 1.7.0 je linuxová binárka Luny UPX balená, ale po
# rozbalení dynamicky linkovaná proti glibc (/lib64/ld-linux-x86-64.so.2) – na
# Alpine/musl kernel/loader ji vůbec nespustí (execve ENOENT, exit 127).
# Samotná binárka se do image nekopíruje (není volně šiřitelná): addon ji při startu
# vezme z /share/luna/luna, nebo stáhne z adresy v nastavení, a uloží do /data.
RUN apt-get update && apt-get install -y --no-install-recommends bash jq curl ca-certificates tzdata python3 \
    && rm -rf /var/lib/apt/lists/*
COPY run.sh /run.sh
COPY webui.py /webui.py
RUN chmod +x /run.sh
CMD ["/run.sh"]
