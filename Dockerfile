FROM debian:bookworm
WORKDIR /app
RUN apt update && \
    apt install -y \
        imagemagick \
		libgtk-3-dev \
        python3 \
        python3-attr \
        python3-gi \
        python3-gi-cairo \
        python3-mastodon \
		libgtk-3-dev
COPY graftbot ./graftbot
COPY graftlib ./graftlib
COPY graft .
COPY bot-mastodon .
CMD ["/app/bot-mastodon"]
