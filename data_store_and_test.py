from environs import Env
from scripts import DoctorFaissIndex

env = Env()
env.read_env()

indexer = DoctorFaissIndex()
indexer.build_index(env.str("DATASET_PATH"))

indexer.load_index()

results = indexer.search("Back pain specialist in Mirpur", k=3)
print("Back pain specialist in Mirpur")

for doc in results:
    print(f"{doc['name']} - {doc['specialization']}")
    print("Available:", ', '.join([a for a in doc['availability'] if a]))
    print("Tags:", ', '.join(doc['tags']))
    print("URL:", doc['doctor_url'])
    print()
