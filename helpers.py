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
        return session, True
