import os

folders = ["trouble_maker", "local_results"]

for d in folders:
    for f in os.listdir(d):
        if f != ".gitignore":
            os.remove(os.path.join(d, f))
