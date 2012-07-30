from gluon import *
from s3 import *

from eden.layouts import S3AddResourceLink
from eden.org import org_organisation_represent
from eden.project import project_project_represent, project_project_represent_no_link

def formset_factory(name, form_function, quantity=1):
    forms = []

    for index in range(0, quantity):
	prefix = "%s_%s_" % (name, index)
	print "prefix: %s" % prefix
	form = form_function(name)

	for e in form.elements():
	    if e["_name"]:
		e["_name"] = "%s%s" % (prefix, e["_name"])
		e["_id"] = "id-%s" % e["_name"]
	forms.append(form)
    return forms

def project_form(name="project_project"):
    s3db = current.s3db
    db = current.db
    T = current.T

    return SQLFORM.factory(
	s3db.project_project,
	Field(
	    "lead_organisation",
	    requires=IS_NOT_EMPTY(),
	    label=T("Lead Organisation"),
	    comment=S3AddResourceLink(
		c="org",
		f="organisation",
		label=T("Add Organisation"),
		title=T("Organization"),
		tooltip=help),
	    widget=S3OrganisationAutocompleteWidget(),
	    represent=org_organisation_represent),
	Field(
	    "parent_project",
	    requires=IS_NULL_OR(
		IS_ONE_OF(
		    db,
		    "project_project.id",
		    project_project_represent_no_link
		)
	    ),
	    represent=project_project_represent,
	    label=B(I(T("Project")))
	),
	Field(
	    "contact_organisation",
	    label=T("Organisation"),
	    widget=S3OrganisationAutocompleteWidget()
	),
	Field(
	    "contact_email",
	    label=T("Email")
	),
	table_name=name
    )

def project_outputs_form(name="project_outputs"):
    T = current.T

    return SQLFORM.factory(
	Field(
	    "output",
	    label=T("Output")#,
	    #~ length=50,
	    #~ requires=IS_LENGTH(maxsize=50),
	    #~ widget = lambda field,value: \
		#~ SQLFORM.widgets.string.widget(
		    #~ field,
		    #~ value,
		    #~ _maxlength=50,
		    #~ _size=50
		#~ )
	),
	Field(
	    "status",
	    label=T("Status")#,
	    #~ length=50,
	    #~ requires=IS_LENGTH(maxsize=50),
	    #~ widget = lambda field,value: \
		#~ SQLFORM.widgets.string.widget(
		    #~ field,
		    #~ value,
		    #~ _maxlength=50,
		    #~ _size=50
		#~ )
	),
	table_name=name
    )

def partner_organisations_form(name="partner_organisations"):
    s3db = current.s3db

    return SQLFORM.factory(
	s3db.project_organisation,
	fields=["organisation_id", "role"],
	table_name=name
    )

def donor_organisations_form(name="donor_organisations"):
    s3db = current.s3db

    return SQLFORM.factory(
	s3db.project_organisation,
	fields=["organisation_id", "amount"],
	table_name=name
    )

def project_files_form(name="project_files"):
    T = current.T

    return SQLFORM.factory(
	Field(
	    "file",
	    "upload",
	    label=T("File")
	),
	Field(
	    "comment",
	    label=T("Comment")
	),
	table_name=name
    )

def project_links_form(name="project_links"):
    T = current.T

    return SQLFORM.factory(
	Field(
	    "url",
	    label=T("URL")
	),
	Field(
	    "comment",
	    label=T("Comment")
	),
	table_name=name
    )
