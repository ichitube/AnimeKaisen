import os, socket, time, sys

def wait_for(host, port, name, timeout=120, interval=2):
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=3):
                print(f"[wait_for] {name} at {host}:{port} is up")
                return
        except OSError:
            if time.time() - start > timeout:
                print(f"[wait_for] Timeout waiting for {name} at {host}:{port}", file=sys.stderr)
                sys.exit(1)
            time.sleep(interval)

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
mongo_host = os.getenv("MONGO_HOST", "mongodb")
mongo_port = int(os.getenv("MONGO_PORT", "27017"))

wait_for(redis_host, redis_port, "Redis")
wait_for(mongo_host, mongo_port, "MongoDB")
print("[wait_for] All dependencies are reachable. Launching bot...")
