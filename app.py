import chromadb
import streamlit as st

from utils.funcs import search_embedding
from streamlit import session_state as _state
from sentence_transformers import SentenceTransformer


# embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# chroma vectorstore
client = chromadb.PersistentClient(path="data")
collection = client.get_collection(name="papers")

pubmed_base_url = "https://pubmed.ncbi.nlm.nih.gov/"

# title image
title_image_path = "images/logo3.png"

st.set_page_config(
    page_title="PaperGPT — A smarter way to search and discover biomedical papers",
    page_icon=title_image_path,
)

# side bar
with st.sidebar:
    st.title(":desktop_computer: Database")
    st.info(
        """
        Number of papers: **29,107**  
        Last updated: **11/13/2023**
        """
    )

    st.title("👋 Contact")
    st.info(
        """
        **[Yuan Tian](https://www.ytiancompbio.com)**:  
        [LinkedIn](https://www.linkedin.com/in/ytiancompbio/) | [Twitter](https://twitter.com/ytiancompbio) | [GitHub](https://github.com/naity)
        """
    )

    st.title(":speech_balloon: Topics")
    st.info(
        """
        - Aging
        - Allergy
        - Biochemistry
        - Bioinformatics and Bioengineering
        - Cancer Biology
        - Cell and Molecular Biology
        - Developmental Biology
        - Genetics and Genomics
        - Microbiology and Immunology
        - Neuroscience
        - Pathology
        - Pharmacology
        - Physiology
        - Structural Biology
        - Virology
        """
    )

    st.title(":open_book: Resources")
    st.info(
        """
        - [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
        - [Hugging Face](https://huggingface.co/)
        - [SentenceTransformers](https://www.sbert.net/)
        """
    )

# title
left_col, right_col = st.columns([1, 2])
with left_col:
    st.image(title_image_path)
with right_col:
    st.markdown('# <span style="color:#ff4500">PaperGPT</span>', unsafe_allow_html=True)
    st.markdown("### A smarter way to search and discover biomedical papers")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    # k
    top_k = st.slider("Number of similar papers", 1, 50, 5, key="top_k")

if "text" not in _state:
    _state.text = ""

# get text
text = st.text_input(
    "Enter paper description 👇",
    key="text",
)


def change_text(text):
    _state.text = text


st.text("Try an example:")
examples = [
    "Single-cell analysis of the immune response in COVID-19 patients",
    "Challenges associated with using CAR-T cells to treat hematologic malignancies or solid tumors",
    "Recent advances in the biological mechanisms of aging and potential interventions to extend lifespan",
]

for i, example in enumerate(examples):
    st.button(example, key=f"example{i}", on_click=change_text, args=(example,))


def get_search_result():
    """Execute search and display results."""
    embedding = model.encode(_state.text).tolist()
    ids, metadatas = search_embedding(collection, embedding, _state.top_k)

    if len(ids) == 0:
        st.warning("No similar papers found.")

    else:
        for paper_id, paper in zip(ids, metadatas):
            st.write("---")
            title = paper["title"]
            abstract = paper["abstract"]
            pubmed_id = paper_id

            paper_url = pubmed_base_url + str(pubmed_id)
            st.markdown(f"### [{title[:-1]}]({paper_url})")
            with st.expander(":point_right: " + "Click to see details", expanded=False):
                # publication date
                st.markdown(
                    ":calendar: Published on " + paper["electronic_publication_date"]
                )
                # journal
                st.markdown(":newspaper: " + paper["journal"])
                # link to pubmed
                st.markdown(":link: [PubMed Link](" + paper_url + ")")
                st.markdown("#### Abstract")
                st.write(abstract)
            st.button(
                "Find similar papers",
                type="primary",
                key=pubmed_id,
                on_click=change_text,
                args=(title + "[SEP]" + abstract,),
            )


container = st.container()

with container:
    if _state.text != "":
        get_search_result()
