
def key_dot_to_list(key_dot):
    """
        "scake.num_cpus" => ["scake", "num_cpus"]
    """
    return key_dot.split(".")
    