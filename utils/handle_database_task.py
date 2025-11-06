def get_table_data(*Djmodels):
    data = {}
    for model in Djmodels:
        model_name = model.__name__.lower()
        data[model_name] = model.objects.all()
    return data

