"""BGE-M3 向量编码器：负责 Dense 与 Sparse 向量的生成"""

from functools import cached_property
from typing import Iterable
from FlagEmbedding import BGEM3FlagModel

from sentiment.engines.contract.settings import get_settings


def _normalize_sparse_vector(sparse_vector: dict) -> dict[int, float]:
    """将稀疏向量字典的键和值分别转换为整数 Token ID 与浮点数权重"""
    return {
        int(token_id): float(weight)
        for token_id, weight in sparse_vector.items()
    }


class VectorEmbedder:
    """封装 BGE-M3 模型的向量编码服务"""

    @cached_property
    def model(self) -> BGEM3FlagModel:
        """按配置惰性创建 BGE-M3 向量模型"""
        settings = get_settings()
        device = settings.INSIGHT_EMBEDDING_DEVICE

        return BGEM3FlagModel(
            settings.INSIGHT_EMBEDDING_MODEL,
            use_fp16="cpu" not in device.lower(),
            devices=device
        )

    def encode(
            self, texts: Iterable[str]
    ) -> list[tuple[list[float], dict[int, float]]]:
        """生成稠密与稀疏向量组合"""
        text_items = list(texts)
        model_output = self.model.encode(
            text_items,
            return_dense=True,
            return_sparse=True
        )

        return [
            (dense.tolist(), _normalize_sparse_vector(sparse))
            for dense, sparse in zip(
                model_output["dense_vecs"], model_output["lexical_weights"]
            )
        ]





if __name__ == '__main__':

    vector_emb=VectorEmbedder()


    print(vector_emb.encode(texts=["我喜欢你"]))



