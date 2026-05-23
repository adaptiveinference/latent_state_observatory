# Avazu CTR Dataset – Usage Guide

## Overview

This dataset comes from the Avazu Click-Through Rate (CTR) prediction task. Each row represents a single ad impression with associated contextual features and a binary label indicating whether the ad was clicked.

- **Task**: Binary classification  
- **Goal**: Predict `click ∈ {0,1}` given contextual features  
- **Size**: ~40M rows  
- **Data type**: Mostly categorical (high cardinality)

---

## Schema

Each row has the following fields:

```
id, click, hour, C1, banner_pos,
site_id, site_domain, site_category,
app_id, app_domain, app_category,
device_id, device_ip, device_model,
device_type, device_conn_type,
C14, C15, C16, C17, C18, C19, C20, C21
```

---

## Field Descriptions

### Label
- **`click`**  
  - Target variable  
  - `1` = clicked, `0` = not clicked  

---

### Identifier
- **`id`**  
  - Unique identifier for each impression  
  - **Not useful for prediction** → should be dropped  

---

### Time
- **`hour`**  
  - Encoded as `YYMMDDHH` (e.g., `14102100` → 2014-10-21 00:00)  
  - Can be decomposed into:
    - `day`
    - `hour_of_day`

---

### Ad / Context Features
- **`C1`**, **`banner_pos`**  
  - Categorical indicators related to ad placement  

---

### Site Features
- **`site_id`**, **`site_domain`**, **`site_category`**  
  - Website where the ad was displayed  

---

### App Features
- **`app_id`**, **`app_domain`**, **`app_category`**  
  - Mobile app context (if applicable)  

---

### Device Features
- **`device_id`**, **`device_ip`**, **`device_model`**  
  - Device identifiers (very high cardinality)  
- **`device_type`**, **`device_conn_type`**  
  - Device metadata (low cardinality)  

---

### Engineered Features
- **`C14` – `C21`**  
  - Preprocessed categorical features  
  - Likely derived from internal feature engineering / bucketing  

---

## Features to Use

### Use for Training
All fields except:
- `id` (drop)
- `click` (target)

Feature set:

```
hour, C1, banner_pos,
site_id, site_domain, site_category,
app_id, app_domain, app_category,
device_id, device_ip, device_model,
device_type, device_conn_type,
C14–C21
```

---

### Recommended Feature Engineering

From `hour`:
- `day = (hour // 100) % 100`
- `hour_of_day = hour % 100`

Treat both as categorical.

---

## Handling Categorical Features

All usable fields are categorical, many with extremely high cardinality.

### Recommended Approach: Feature Hashing

---

## Hashing Strategy

### 1. Create feature tokens

```
site_id=1fbe01fe
device_model=44956a24
C1=1005
```

Always prefix with field name.

---

### 2. Hash to integer index

```python
import mmh3

def hash_feature(field, value, num_buckets):
    token = f"{field}={value}"
    return mmh3.hash(token, signed=False) % num_buckets
```

---

### 3. Bucket size

Typical:
- Small fields: `2^12 – 2^16`
- Large fields: `2^18 – 2^22`

Simple default:
```
num_buckets = 2**18
```

---

### 4. Per-field hashing

```python
site_id_idx = hash_feature("site_id", row["site_id"], 2**20)
device_model_idx = hash_feature("device_model", row["device_model"], 2**18)
```

---

### 5. Why prefix matters

Without prefix:
```
"1005" from C1
"1005" from C17
```

With prefix:
```
"C1=1005"
"C17=1005"
```

---

## Model Input Representation

After hashing:
- Each field → integer index
- Feed into embeddings or linear models

## Embeddings for Hashed Categorical Features

### Overview

After hashing, each categorical feature becomes an integer index:

```
site_id=1fbe01fe → 483920
```

This integer has no inherent meaning. An **embedding** maps this index to a dense vector:

```
483920 → [0.12, -0.8, ..., 0.03]
```

---

### What Embeddings Do

- Convert discrete IDs → continuous vectors  
- Reduce dimensionality (millions → ~16)  
- Learn similarity between categories  
- Enable generalization across sparse features  

Mathematically:

```
Embedding(i) = E[i]
```

Where:
- `i` = hashed index  
- `E` = embedding matrix (num_buckets × dim)  

---

### Implementation (PyTorch)

#### Define embedding

```python
import torch.nn as nn

num_buckets = 2**20
embedding_dim = 16

emb = nn.Embedding(num_buckets, embedding_dim)
```

#### Lookup

```python
idx = hash_feature("site_id", value, num_buckets)
vec = emb(torch.tensor([idx]))
```

---

### Multiple Features

For each field:

```python
vecs = [
    emb_site_id(site_id_idx),
    emb_device(device_idx),
    ...
]
```

Combine:

```python
x = torch.cat(vecs, dim=1)
```

Feed into MLP.

---

### Best Practices

- Use **one embedding table per field**  
- Use **16-dim embeddings** to start  
- Always **prefix before hashing** (`field=value`)  
- Use large enough hash space (e.g., `2^18–2^20`)  

---

### Summary

- Hashing → scalable IDs  
- Embeddings → learnable representations  
- Together → efficient modeling for large categorical datasets


---

## Recommended Starting Point

### Baseline
- Feature hashing
- Logistic regression

### Main Model
- Per-field hashing
- Embeddings (e.g., 16-dim)
- Small MLP

---

## Notes

- Dataset is time-ordered → use time-aware splits  
- Avoid random shuffling across time  
- Expect class imbalance (~17% positive)  
- Do not load entire dataset into memory  

---

## Summary

- Treat all features as categorical  
- Drop `id`, predict `click`  
- Use hashing with field prefixes  
- Use embeddings for scalable modeling  
- Respect temporal structure  
