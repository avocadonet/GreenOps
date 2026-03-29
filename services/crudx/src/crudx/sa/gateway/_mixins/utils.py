def get_select_by_id_params[Model](model: Model, id_attr: str | tuple[str]):
    if isinstance(id_attr, tuple):
        return {attr: getattr(model, attr) for attr in id_attr}
    if isinstance(id_attr, str):
        return {id_attr: getattr(model, id_attr)}
