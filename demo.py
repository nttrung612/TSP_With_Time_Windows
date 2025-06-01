import time

s = time.time()

time.sleep(5)  # Simulating some processing time

print(time.time() - s < 6)