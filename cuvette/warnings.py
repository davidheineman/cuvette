import warnings

def suppress_beaker_warnings():
    warnings.filterwarnings(
        "ignore",
        message="Found unknown field.*for data model.*This may be a newly added field.*",
        category=RuntimeWarning,
        module="beaker.util"
    )


def setup_cuvette_warnings():
    suppress_beaker_warnings()
