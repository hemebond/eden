import json
T = current.T


def index():

    def _regional():
        resource = s3mgr.define_resource("org", "organisation")
        f = (s3base.S3FieldSelector("project.id") != None) & \
            (s3base.S3FieldSelector("organisation_type_id$name").anyof(["Regional"]))
        resource.add_filter(f)

        field_list = [
            "id",
            "name",
            "acronym",
            (T("Type"), "organisation_type_id$name"),
            "website",
            "region",
            "year",
            (T("Notes"), "comments")
        ]
        return (resource, field_list)

    def _groups():
        resource = s3mgr.define_resource("org", "organisation")
        f = s3base.S3FieldSelector("project.id") != None
        resource.add_filter(f)

        field_list = [
            "id",
            "name",
            "acronym",
            (T("Type"), "organisation_type_id$name"),
            "year",
            #"address",
            (T("Notes"), "comments")
        ]
        return (resource, field_list)

    tables = []
    table = request.vars.get("table", None)

    if table is None or table=="regional":
        resource, field_list = _regional()
        tables.append(_table("regional", resource, field_list))

    if table is None or table=="groups":
        resource, field_list = _groups()
        tables.append(_table("groups", resource, field_list))

    if table is not None:
        s3db.configure(resource.tablename,
                       list_fields = field_list)

        output = s3_rest_controller(resource.prefix, resource.name)
        return output

    return dict(tables=tables,
                appname=current.request.application)


def _table(name, resource, field_list, limit=10, orderby="name"):
    fields = []
    cols = []
    for field_name in field_list:
        if isinstance(field_name, tuple):
            field_label = field_name[0]
            field_name = field_name[1]
        else:
            field_label = None

        fs = s3base.S3FieldSelector(field_name)
        list_field = fs.resolve(resource)

        if list_field.field != None:
            field = list_field.field
            if field.type=="integer":
                field_type = "numeric"
            else:
                field_type = "string"
        else:
            field = field_name
            field_type = "string"

        if field_label is None:
            if list_field.field is not None:
                field_label = field.label
            else:
                field_label = " ".join([w.capitalize() for w in field_name.split(".")[-1].split("_")])

        fields.append(field)
        cols.append({
            "name": field_name,
            "label": field_label,
            "type": field_type
        })

        if orderby and str(orderby)==str(field_name):
            orderby=field

    rows = resource.sqltable(fields=field_list,
                             limit=limit,
                             orderby=orderby,
                             as_rows=True)

    if rows:
        table_rows = []
        for row in rows:
            table_row = []

            for field in fields:
                if isinstance(field, str):
                    value = row[resource.tablename][field]
                else:
                    value = row[field]

                table_row.append(value)

            table_rows.append(table_row)
    else:
        table_rows = []

    options = json.dumps({
        "iDisplayLength": limit,
        "iDeferLoading": len(resource.load()),
        "bProcessing": True,
        "bServerSide": True,
        "sAjaxSource": "index.aadata?table=%s" % name,
        "aoColumnDefs": [
            {
                "bVisible": False,
                "aTargets": [0]
            }
        ],
        "aoColumns": [{"sName": col["name"], "sType": col["type"]} for col in cols],
		"sDom": '<frl><"dataTable_table"t><pi>',
    })

    table = Storage(
        cols=cols,
        rows=table_rows,
        options=options
    )

    return table
