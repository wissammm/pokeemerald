import random
import os

def generate_unique_id():
    used_ids = set()
    if os.path.exists("used_ids.txt"):
        with open("used_ids.txt", "r") as file:
            used_ids = set(file.read().splitlines())
    
    while True:
        unique_id = str(random.randint(100000, 999999))
        if unique_id not in used_ids:
            with open("used_ids.txt", "a") as file:
                file.write(unique_id + "\n")
            return unique_id

if __name__ == "__main__":
    unique_id = generate_unique_id()
    print(unique_id)