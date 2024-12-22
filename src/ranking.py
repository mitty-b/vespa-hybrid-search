from vespa.package import (
    RankProfile,
    Function,
    GlobalPhaseRanking,
)

def create_rank_profiles():
    return [
        RankProfile(
            name="bm25",
            inputs=[("query(q)", "tensor<float>(x[384])")],
            functions=[
                Function(name="bm25sum", expression="bm25(title) + bm25(body)")
            ],
            first_phase="bm25sum",
        ),
        RankProfile(
            name="semantic",
            inputs=[("query(q)", "tensor<float>(x[384])")],
            first_phase="closeness(field, embedding)",
        ),
        RankProfile(
            name="fusion",
            inherits="bm25",
            inputs=[("query(q)", "tensor<float>(x[384])")],
            first_phase="closeness(field, embedding)",
            global_phase=GlobalPhaseRanking(
                expression="reciprocal_rank_fusion(bm25sum, closeness(field, embedding))",
                rerank_count=1000,
            ),
        ),
    ]