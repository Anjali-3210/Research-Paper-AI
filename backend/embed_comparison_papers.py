from embed_documents import embed_paper


embed_paper(
    "../data/paper1.pdf",
    "comparison_paper1"
)

embed_paper(
    "../data/paper2.pdf",
    "comparison_paper2"
)

print("Both comparison papers indexed successfully!")