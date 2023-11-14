import time
from Bio import Entrez
from tqdm import tqdm


def search_and_download(query, out_file, num_papers=2500, batch_size=100, sleep=1):
    """Search and download a list of papers related to query from PubMed"""
    Entrez.email = "admin@gmail.com"

    # search for papers
    search_results = Entrez.read(
        Entrez.esearch(
            db="pubmed", term=query, reldate=365, datetype="pdat", usehistory="y"
        )
    )
    count = int(search_results["Count"])

    # don't exceed num_papers
    count = min(count, num_papers)
    print(f"Found {count} results for {query}")

    # download papers
    with open(out_file, "a") as out_handle:
        for start in tqdm(range(0, count, batch_size)):
            attempt = 0
            while attempt < 5:
                try:
                    attempt += 1
                    fetch_handle = Entrez.efetch(
                        db="pubmed",
                        rettype="medline",
                        retmode="text",
                        retstart=start,
                        retmax=batch_size,
                        webenv=search_results["WebEnv"],
                        query_key=search_results["QueryKey"],
                    )
                    data = fetch_handle.read()
                    fetch_handle.close()
                    out_handle.write(data)
                    break
                except:
                    print(f"Attempt {attempt} failed. Retrying in {sleep} seconds...")
                    time.sleep(sleep)
                    continue


def upsert_to_collection(collection, ids, embeddings, metadatas, batch_size=10000):
    """
    Upsert items to collection.
    New items will be added, existing items will be updated.
    """
    assert (
        len(ids) == len(embeddings) == len(metadatas)
    ), "The lengths of ids, embeddings, and metadatas much match"

    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            embeddings=embeddings[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )


def search_embedding(collection, embedding, top_k):
    results = collection.query(
        query_embeddings=embedding, n_results=top_k, include=["metadatas"]
    )

    # return the first items
    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    return ids, metadatas
