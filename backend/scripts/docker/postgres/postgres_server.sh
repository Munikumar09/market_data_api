#!/bin/bash

# PostgreSQL configuration variables
POSTGRES_COMPOSE_SERVICE="postgres_container"  # Replace with your PostgreSQL service name in Docker Compose
POSTGRES_COMPOSE_PATH="../../../app/configs/docker/postgres/postgres.yaml"

# Function to check if a Docker container is running
is_container_running() {
    docker ps -f name=$1 --format '{{.Names}}' | grep -w $1 > /dev/null
}

# Function to start PostgreSQL
start_postgres() {
    if ! is_container_running $POSTGRES_COMPOSE_SERVICE; then
        echo "Starting PostgreSQL container..."
        docker compose -f $POSTGRES_COMPOSE_PATH up -d
        echo "Waiting for PostgreSQL to start..."
        sleep 10 # Give PostgreSQL some time to start
    else
        echo "PostgreSQL container is already running."
    fi
}

# Function to stop PostgreSQL
stop_postgres() {
    if is_container_running $POSTGRES_COMPOSE_SERVICE; then
        echo "Stopping PostgreSQL container... ${POSTGRES_COMPOSE_PATH}"
        docker compose -f $POSTGRES_COMPOSE_PATH down
    else
        echo "PostgreSQL container is not running."
    fi
}

# Check arguments
if [ $# -eq 0 ]; then
    echo "Error: You must provide --start or --stop as an argument."
    exit 1
fi

case $1 in
    --start)
        start_postgres
        ;;
    --stop)
        stop_postgres
        ;;
    *)
        echo "Error: Invalid argument. Use --start or --stop."
        exit 1
        ;;
esac
