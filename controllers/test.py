import json
T = current.T

from s3.s3utils import S3SQLTable, S3DataTable


def index():
    cols = [{'name': 'id', 'label': 'Id'},
            {'name': 'col_1', 'label': 'Col 1'}]
    rows = [[u'1', u'Val 1']]
    row_actions = [{"label": T("Activate"),
                    "url": URL(f="schedule_parser",
                               args="[id]"),
                    "restrict": [1,]}]
    bulk_actions = [("delete", "Delete")]

    table = S3DataTable({},
                        cols,
                        rows,
                        row_actions=row_actions,
                        bulk_actions=bulk_actions)
    #~ table = S3SQLTable(cols,
                       #~ rows)

    return {"table": table, "appname": "eden"}


def old():

    def _regional():
        resource = s3mgr.define_resource("org", "organisation")
        #f = (s3base.S3FieldSelector("project.id") != None) & \
        #    (s3base.S3FieldSelector("organisation_type_id$name").anyof(["Regional"]))
        #resource.add_filter(f)

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
        #f = s3base.S3FieldSelector("project.id") != None
        #resource.add_filter(f)

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
        else:
            field = field_name

        if field_label is None:
            if list_field.field is not None:
                field_label = field.label
            else:
                field_label = " ".join([w.capitalize() for w in field_name.split(".")[-1].split("_")])

        fields.append(field)
        cols.append({
            "name": field_name,
            "label": field_label
        })

        if orderby and str(orderby)==str(field_name):
            orderby=field

    rows = resource.sqltable(fields=field_list,
                             limit=limit,
                             orderby=orderby,
                             as_page=True)

    if rows is None:
        rows = []

    options = json.dumps({
        "iDisplayLength": limit,
        "iDeferLoading": len(resource.load()),
        "bProcessing": True,
        "bServerSide": True,
        "sAjaxSource": "index.aaData?table=%s" % name,
        "aoColumnDefs": [
            {
                "bVisible": False,
                "aTargets": [0]
            }
        ],
        "aoColumns": [{"sName": col["name"]} for col in cols],
		"sDom": 'frltpi',
    })

    table = Storage(
        cols=cols,
        rows=rows,
        options=options,
        classes="dataTable display"
    )

    return table
