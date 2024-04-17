FROM debian:bullseye-slim AS BUILDER


ADD https://github.com/Kilerd/staple/releases/download/0.3.2/staple-ubuntu.tar.gz staple-ubuntu.tar.gz

RUN tar -xvzf staple-ubuntu.tar.gz

RUN cp staple /bin/staple
RUN chmod +x /bin/staple

WORKDIR /app

COPY . /app
RUN staple build
RUN ls -l /app


FROM busybox:1.35

# Create a non-root user to own the files and run our server
RUN adduser -D static
USER static
WORKDIR /home/static

# Copy the static website
# Use the .dockerignore file to control what ends up inside the image!
COPY --from=BUILDER /app/public /home/static

EXPOSE 3000
# Run BusyBox httpd
CMD ["busybox", "httpd", "-f", "-v", "-p", "3000"]