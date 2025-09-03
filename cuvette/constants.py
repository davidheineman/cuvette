CLUSTERS = [
    # (pretty name, cluster name, description, default # GPUs)
    (
        "Any CPU  (       CPU, 1wk lim, WEKA)",
        [
            "ai2/phobos-cirrascale",  # fast session starts
        ],
        "Any cluster supporting 1 week CPU sessions",
        0,
    ),
    (
        "Any L40s ( 40GB L40s, 1dy lim, WEKA)",
        [
            "ai2/neptune-cirrascale",
            "ai2/triton-cirrascale",
        ],
        "Any cluster with L40s or A100s",
        1,
    ),
    (
        "Any A100 ( 80GB A100, 1dy lim, WEKA)",
        [
            "ai2/saturn-cirrascale",
        ],
        "Any cluster with 1 week A100 sessions",
        1,
    ),
    (
        "Any H100 ( 80GB H100, 4hr lim, WEKA)",
        [
            "ai2/ceres-cirrascale",
            "ai2/jupiter-cirrascale-2",
        ],
        "Any cluster with 2 hour H100 sessions",
        1,
    ),
    (
        "Any B200 (192GB B200, 4hr lim, WEKA)",
        [
            "ai2/titan-cirrascale",
        ],
        "Any cluster with 2 hour B200 sessions",
        1,
    ),
    (
        "Phobos   (       CPU, 1wk lim, WEKA)",
        "ai2/phobos-cirrascale",
        "Debugging and data transfers - No GPUs, Ethernet (50 Gbps/server), WEKA storage, 1 week timeout",
        0,
    ),
    (
        "Saturn   ( 80GB A100, 1dy lim, WEKA)",
        "ai2/saturn-cirrascale",
        "Small experiments before using Jupiter - 208 NVIDIA A100 (80 GB) GPUs, Ethernet (50 Gbps/server), WEKA storage, 1 week timeout",
        1,
    ),
    (
        "Ceres    ( 80GB H100, 4hr lim, WEKA)",
        "ai2/ceres-cirrascale",
        "Small distributed jobs - 88 NVIDIA H100 GPUs (80 GB), 4x NVIDIA InfiniBand (200 Gbps/GPU), WEKA storage, 2 hour timeout",
        1,
    ),
    (
        "Jupiter  ( 80GB H100, 4hr lim, WEKA)",
        "ai2/jupiter-cirrascale-2",
        "Large distributed jobs - 1024 NVIDIA H100 (80 GB) GPUs, 8x NVIDIA InfiniBand (400 Gbps/GPU), WEKA storage, 2 hour timeout",
        1,
    ),
    (
        "Titan    (192GB B200, 4hr lim, WEKA)",
        "ai2/titan-cirrascale",
        "Distributed jobs - 96 NVIDIA B200 (192GB) GPUs, 8x NVIDIA InfiniBand (400 Gbps/GPU), 2 hour timeout",
        1,
    ),
    (
        "Neptune  ( 40GB L40s, 1dy lim, WEKA)",
        "ai2/neptune-cirrascale",
        "Small experiments (≤ 40 GB memory) - 112 NVIDIA L40 (40 GB) GPUs, Ethernet (50 Gbps/server), WEKA storage, 1 week timeout",
        1,
    ),
    (
        "Triton   ( 40GB L40s, 1dy lim, WEKA)",
        "ai2/triton-cirrascale",
        "Session-only - 16 NVIDIA L40 (40 GB) GPUs, Ethernet (50 Gbps/server), WEKA storage, 1 week timeout",
        1,
    ),
    (
        "Augusta  ( 80GB H100, 4hr lim, GCS)",
        "ai2/augusta-google-1",
        "Large distributed jobs - 1280 NVIDIA H100 (80 GB) GPUs, TCPXO (200 Gbps/server), Google Cloud Storage, 2 hour timeout",
        1,
    ),
    (
        "Neptune CPU",
        [
            "ai2/neptune-cirrascale",
        ],
        "1 week CPU session",
        0,
    ),
    (
        "Triton CPU",
        [
            "ai2/triton-cirrascale",
        ],
        "1 week CPU session",
        0,
    ),
    (
        "Saturn CPU",
        [
            "ai2/saturn-cirrascale",
        ],
        "1 day CPU session",
        0,
    ),
]


NEW_CLUSTER_ALIASES = {
    "ai2/allennlp": "ai2/allennlp-elanding-a100-40g",
    "ai2/allennlp-dev-a100-sea": "ai2/allennlp-elanding-a100-40g",
    "ai2/augusta-batch-h100-dsm-tcpxo": "ai2/augusta-google-1",
    "ai2/augusta":"ai2/augusta-google-1",
    "ai2/ceres-dev-h100-aus-ib": "ai2/ceres-cirrascale",
    "ai2/ceres":"ai2/ceres-cirrascale",
    "ai2/jupiter-batch-h100-aus-ib": "ai2/jupiter-cirrascale-2",
    "ai2/jupiter":"ai2/jupiter-cirrascale-2",
    "ai2/neptune-dev-l40-aus": "ai2/neptune-cirrascale",
    "ai2/neptune":"ai2/neptune-cirrascale",
    "ai2/phobos-dev-aus": "ai2/phobos-cirrascale",
    "ai2/phobos":"ai2/phobos-cirrascale",
    "ai2/prior-dev-a6000-sea": "ai2/prior-elanding",
    "ai2/prior":"ai2/prior-elanding",
    "ai2/prior-rtx8000":"ai2/prior-elanding-rtx8000",
    "ai2/prior-dev-rtx8000-sea": "ai2/prior-elanding-rtx8000",
    "ai2/rhea-dev-a6000-aus": "ai2/rhea-cirrascale",
    "ai2/rhea":"ai2/rhea-cirrascale",
    "ai2/saturn-dev-a100-aus": "ai2/saturn-cirrascale",
    "ai2/saturn":"ai2/saturn-cirrascale",
    "ai2/titan-batch-b200-aus-ib": "ai2/titan-cirrascale",
    "ai2/titan":"ai2/titan-cirrascale",
    "ai2/triton-dev-l40-aus": "ai2/triton-cirrascale",
    "ai2/triton":"ai2/triton-cirrascale",
}