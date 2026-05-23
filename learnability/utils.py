import numpy as np
import mmh3

GLOBAL_HASH_BUCKET_SIZE = 2**20

# ===================================
# Entropy of binary distribution
# ===================================
def _binary_entropy_bits(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-12, 1.0 - 1e-12)
    return -(p * np.log2(p) + (1.0 - p) * np.log2(1.0 - p))

# ===================================
# Hash categorical feature
# ===================================
def hash_feature(s: str, num_buckets: int) -> int:
    return mmh3.hash(s, signed=False) % num_buckets


# ===================================
# Avazu CTR helpers
# ===================================
AVAZU_COLUMNS = [
    "id", "click", "hour", "C1", "banner_pos",
    "site_id", "site_domain", "site_category",
    "app_id", "app_domain", "app_category",
    "device_id", "device_ip", "device_model",
    "device_type", "device_conn_type",
    "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21",
]

AVAZU_TARGET_COLUMN = "click"
AVAZU_DROP_COLUMNS = ["id", "click","hour_idx"]
AVAZU_FEATURE_COLUMNS = [c for c in AVAZU_COLUMNS if c not in AVAZU_DROP_COLUMNS]


def hash_feature_value(field: str, value, num_buckets: int = GLOBAL_HASH_BUCKET_SIZE) -> int:
    """Hash one categorical Avazu feature as field=value -> bucket index.

    Do not use Python's built-in hash(); it is randomized across processes.
    """
    return hash_feature(f"{field}={value}", num_buckets=num_buckets)


def hash_avazu_frame(df, feature_columns=None, num_buckets: int = GLOBAL_HASH_BUCKET_SIZE, dtype=np.int64):
    """Convert an Avazu pandas DataFrame into hashed categorical IDs and labels.

    Returns
    -------
    X : np.ndarray, shape (N, num_features), integer dtype
        Hashed categorical indices. This can be fed directly to
        AvazuEmbeddingMLPClassifier, which will learn embeddings.
    y : np.ndarray, shape (N,)
        Binary click labels.
    feature_columns : list[str]
        Column order used to construct X.
    """
    if feature_columns is None:
        feature_columns = [c for c in df.columns if c not in AVAZU_DROP_COLUMNS]

    X = np.empty((len(df), len(feature_columns)), dtype=dtype)
    for j, field in enumerate(feature_columns):
        # Prefixing with field name prevents cross-field collisions.
        X[:, j] = [hash_feature_value(field, v, num_buckets) for v in df[field].values]

    y = df[AVAZU_TARGET_COLUMN].to_numpy(dtype=np.int64) if AVAZU_TARGET_COLUMN in df.columns else None
    return X, y, list(feature_columns)


if __name__ == "__main__":
    x = "site_id=1fbe01fe"
    idx = hash_feature(x, GLOBAL_HASH_BUCKET_SIZE)
    print(idx)
