def format_parameters(params: dict):
    list_params = list()
    for k, v in params.items():
        list_params.append(f"--{k}")
        list_params.append(f"{v}")

    return list_params

def format_command(params: dict):
    list_params = list()
    for k, v in params.items():
        list_params.append(f"{k}")
        list_params.append(f"{v}")

    return list_params