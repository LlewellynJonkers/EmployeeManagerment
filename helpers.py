entry_statuses = [
    "present",
    "absent",
    "annual leave",
    "sick leave",
    "school closed",
    "family resp leave",
    "special leave",
    "unpaid leave",
    "pre-natal leave",
    "maternity leave",
    "parternal leave",
    "not active",
    "other"
]
def get_or_create(session,model,defaults=None,**kwargs):
    defaults = defaults if defaults else {}
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        for k, v in defaults.items():
            setattr(instance,k,v)
        return instance, False
    else:
        params = dict(kwargs)
        params.update(defaults)
        instance = model(**params)
        session.add(instance)
        return instance, True
