
# heldout = calib + test = 50%
DEFAULT_DATA_SPLIT = {
    "train"     : 0.50,       # 50% training
    "calib"     : 0.25,       # 25% temperature calibration
    "test"      : 0.25,       # 25% on test
}


MODEL_LIBRARY_BASE = {
    "model": "mlp",
    "device": "cpu",
    "num_epochs": 50,
    "batch_size": 256,
    "learning_rate": 1e-3,
    "weight_decay": 1e-4,
    "seed": 42,

    "mlp": {
        "input_dim": None,
        "out_classes": None,
        "num_hidden_layers": 2,
        "hidden_layer_width": 128,
        "dropout": 0.0,
        "activation": "relu",
    },

    # Avazu-specific neural model.
    # Input X should be integer hashed categorical IDs with shape (N, num_fields).
    # embedding_dim is d.
    "avazu_embedding_mlp": {
        "num_fields": 22,
        "out_classes": 2,
        "num_buckets": 2**20,
        "embedding_dim": 16,
        "num_hidden_layers": 2,
        "hidden_layer_width": 128,
        "dropout": 0.1,
        "activation": "relu",
    },

    "gmm": {
        "input_dim": None,
        "out_classes": None,
        "num_mixtures": 4,
        "init_std": 1.0,
        "min_var": 1e-4,
        "class_prior_logits_init": 0.0,
    },

    "transformer": {
        "input_dim": None,
        "out_classes": None,
        "seq_len": None,
        "d_model": 128,
        "nhead": 8,
        "num_layers": 4,
        "dim_feedforward": 512,
        "dropout": 0.1,
        "use_learned_pos_emb": True,
        "input_proj_bias": True,
    },

    "gbt": {
        "backend": "sklearn_hist",
        "out_classes": 2,
        "max_iter": 200,
        "learning_rate": 0.05,
        "max_leaf_nodes": 31,
        "max_depth": None,
        "l2_regularization": 0.0,
        "min_samples_leaf": 20,
        "validation_fraction": 0.1,
        "n_iter_no_change": 20,
        "random_state": 42,
    },
}

MLP_SMALL = {
    **MODEL_LIBRARY_BASE,
    "model": "mlp",
    "mlp": {
        **MODEL_LIBRARY_BASE["mlp"],
        "num_hidden_layers": 2,
        "hidden_layer_width": 64,
        "dropout": 0.1,
        "activation": "relu",
    },
}

MLP_MEDIUM = {
    **MODEL_LIBRARY_BASE,
    "model": "mlp",
    "mlp": {
        **MODEL_LIBRARY_BASE["mlp"],
        "num_hidden_layers": 4,
        "hidden_layer_width": 64,
        "dropout": 0.1,
        "activation": "relu",
    },
}

AVAZU_EMBEDDING_MLP_SMALL = {
    **MODEL_LIBRARY_BASE,
    "model": "avazu_embedding_mlp",
    "avazu_embedding_mlp": {
        **MODEL_LIBRARY_BASE["avazu_embedding_mlp"],
        "embedding_dim": 8,
        "num_hidden_layers": 2,
        "hidden_layer_width": 64,
        "dropout": 0.1,
    },
}

AVAZU_EMBEDDING_MLP_MEDIUM = {
    **MODEL_LIBRARY_BASE,
    "model": "avazu_embedding_mlp",
    "avazu_embedding_mlp": {
        **MODEL_LIBRARY_BASE["avazu_embedding_mlp"],
        "embedding_dim": 16,
        "num_hidden_layers": 3,
        "hidden_layer_width": 128,
        "dropout": 0.1,
    },
}

AVAZU_EMBEDDING_MLP_LARGE = {
    **MODEL_LIBRARY_BASE,
    "model": "avazu_embedding_mlp",
    "avazu_embedding_mlp": {
        **MODEL_LIBRARY_BASE["avazu_embedding_mlp"],
        "embedding_dim": 32,
        "num_hidden_layers": 4,
        "hidden_layer_width": 256,
        "dropout": 0.15,
    },
}

GMM_SMALL = {
    **MODEL_LIBRARY_BASE,
    "model": "gmm",
    "gmm": {
        **MODEL_LIBRARY_BASE["gmm"],
        "num_mixtures": 2,
        "init_std": 1.0,
        "min_var": 1e-4,
    },
}

GMM_MEDIUM = {
    **MODEL_LIBRARY_BASE,
    "model": "gmm",
    "gmm": {
        **MODEL_LIBRARY_BASE["gmm"],
        "num_mixtures": 8,
        "init_std": 1.0,
        "min_var": 1e-4,
    },
}

TRANSFORMER_SMALL = {
    **MODEL_LIBRARY_BASE,
    "model": "transformer",
    "transformer": {
        **MODEL_LIBRARY_BASE["transformer"],
        "d_model": 64,
        "nhead": 4,
        "num_layers": 2,
        "dim_feedforward": 128,
        "dropout": 0.1,
    },
}

TRANSFORMER_MEDIUM = {
    **MODEL_LIBRARY_BASE,
    "model": "transformer",
    "transformer": {
        **MODEL_LIBRARY_BASE["transformer"],
        "d_model": 128,
        "nhead": 8,
        "num_layers": 4,
        "dim_feedforward": 512,
        "dropout": 0.1,
    },
}

GBT_SMALL = {
    **MODEL_LIBRARY_BASE,
    "model": "gbt",
    "gbt": {
        **MODEL_LIBRARY_BASE["gbt"],
        "max_iter": 100,
        "learning_rate": 0.08,
        "max_leaf_nodes": 15,
        "min_samples_leaf": 50,
    },
}

GBT_MEDIUM = {
    **MODEL_LIBRARY_BASE,
    "model": "gbt",
    "gbt": {
        **MODEL_LIBRARY_BASE["gbt"],
        "max_iter": 300,
        "learning_rate": 0.05,
        "max_leaf_nodes": 31,
        "min_samples_leaf": 20,
    },
}

GBT_LADDER = {
    "model": "gbt",
    "gbt_00_stump": {
        "backend": "sklearn_hist",
        "out_classes": 2,
        "max_iter": 50,
        "learning_rate": 0.08,
        "max_leaf_nodes": 3,
        "max_depth": 1,
        "l2_regularization": 1e-2,
        "min_samples_leaf": 200,
        "validation_fraction": 0.1,
        "n_iter_no_change": 10,
        "random_state": 42,
    },

    "gbt_01_tiny": {
        "backend": "sklearn_hist",
        "out_classes": 2,
        "max_iter": 100,
        "learning_rate": 0.08,
        "max_leaf_nodes": 7,
        "max_depth": 3,
        "l2_regularization": 1e-3,
        "min_samples_leaf": 100,
        "validation_fraction": 0.1,
        "n_iter_no_change": 15,
        "random_state": 42,
    },

    "gbt_02_small": {
        "backend": "sklearn_hist",
        "out_classes": 2,
        "max_iter": 150,
        "learning_rate": 0.06,
        "max_leaf_nodes": 15,
        "max_depth": None,
        "l2_regularization": 1e-4,
        "min_samples_leaf": 50,
        "validation_fraction": 0.1,
        "n_iter_no_change": 20,
        "random_state": 42,
    },

    "gbt_03_medium": {
        "backend": "sklearn_hist",
        "out_classes": 2,
        "max_iter": 250,
        "learning_rate": 0.04,
        "max_leaf_nodes": 31,
        "max_depth": None,
        "l2_regularization": 1e-5,
        "min_samples_leaf": 30,
        "validation_fraction": 0.1,
        "n_iter_no_change": 25,
        "random_state": 42,
    },

    "gbt_04_large": {
        "backend": "sklearn_hist",
        "out_classes": 2,
        "max_iter": 400,
        "learning_rate": 0.03,
        "max_leaf_nodes": 63,
        "max_depth": None,
        "l2_regularization": 1e-6,
        "min_samples_leaf": 20,
        "validation_fraction": 0.1,
        "n_iter_no_change": 30,
        "random_state": 42,
    },

    "gbt_05_xlarge": {
        "backend": "sklearn_hist",
        "out_classes": 2,
        "max_iter": 700,
        "learning_rate": 0.02,
        "max_leaf_nodes": 127,
        "max_depth": None,
        "l2_regularization": 0.0,
        "min_samples_leaf": 10,
        "validation_fraction": 0.1,
        "n_iter_no_change": 40,
        "random_state": 42,
    },
}

SKLEARN_HIST_LADDER = {
    "model": "sklearn_hist",
    "hist_stump": dict(max_iter=75, learning_rate=0.08, max_leaf_nodes=3,  min_samples_leaf=200, l2_regularization=1e-2),
    "hist_small": dict(max_iter=150, learning_rate=0.06, max_leaf_nodes=15, min_samples_leaf=100, l2_regularization=1e-3),
    "hist_medium": dict(max_iter=300, learning_rate=0.04, max_leaf_nodes=31, min_samples_leaf=50, l2_regularization=1e-4),
}

LIGHTGBM_LADDER = {
    "model": "lightgbm",
    "lgbm_small": dict(
        objective="binary",
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        max_depth=-1,
        min_child_samples=100,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_lambda=1.0,
    ),

    "lgbm_medium": dict(
        objective="binary",
        n_estimators=700,
        learning_rate=0.03,
        num_leaves=63,
        max_depth=-1,
        min_child_samples=50,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=0.3,
    ),

    "lgbm_large": dict(
        objective="binary",
        n_estimators=1200,
        learning_rate=0.02,
        num_leaves=127,
        max_depth=-1,
        min_child_samples=20,
        subsample=1.0,
        colsample_bytree=1.0,
        reg_lambda=0.0,
    ),
}

CATBOOST_LADDER = {
    "model": "catboost",
    "cat_small": dict(
        loss_function="Logloss",
        eval_metric="Logloss",
        iterations=300,
        learning_rate=0.05,
        depth=4,
        l2_leaf_reg=10.0,
        random_seed=42,
        verbose=False,
    ),

    "cat_medium": dict(
        loss_function="Logloss",
        eval_metric="Logloss",
        iterations=700,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=5.0,
        random_seed=42,
        verbose=False,
    ),

    "cat_large": dict(
        loss_function="Logloss",
        eval_metric="Logloss",
        iterations=1200,
        learning_rate=0.02,
        depth=8,
        l2_leaf_reg=3.0,
        random_seed=42,
        verbose=False,
    ),

    "cat_xlarge": dict(
        loss_function="Logloss",
        eval_metric="Logloss",
        iterations=2000,
        learning_rate=0.015,
        depth=10,
        l2_leaf_reg=1.0,
        random_seed=42,
        verbose=False,
    ),
}
