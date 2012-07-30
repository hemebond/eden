# -*- coding: utf-8 -*-

from os import path

try:
    import json # try stdlib (Python 2.6)
except ImportError:
    try:
        import simplejson as json # try external module
    except:
        import gluon.contrib.simplejson as json # fallback to pure-Python module

from gluon import *
from gluon.storage import Storage
from s3 import *

from eden.layouts import S3AddResourceLink
from eden.org import org_organisation_represent
from eden.project import project_project_represent, project_project_represent_no_link
import forms
import forms2

# =============================================================================
def INPUT_BTN(**attributes):
    """
        Utility function to create a styled button
    """

    return SPAN(INPUT(_class = "button-right",
                      **attributes),
                _class = "button-left")

# =============================================================================
class index():
    """ Custom Home Page """

    def __call__(self):

        request = current.request
        response = current.response

        response.title = current.deployment_settings.get_system_name()
        view = path.join(request.folder, "private", "templates",
                         "DRRPP", "views", "index.html")
        try:
            # Pass view as file not str to work in compiled mode
            response.view = open(view, "rb")
        except IOError:
            from gluon.http import HTTP
            raise HTTP("404", "Unable to open Custom View: %s" % view)

        T = current.T
        appname = request.application

        home_img = IMG(_src="/%s/static/themes/DRRPP/img/home_img.jpg" % appname,
                       _id="home_img")
        home_page_img = IMG(_src="/%s/static/themes/DRRPP/img/home_page_img.png" % appname,
                            _id="home_page_img")
        home_map_img = IMG(_src="/%s/static/themes/DRRPP/img/home_map_img.png" % appname,
                           _id="home_map_img")

        list_img = A(IMG(_src="/%s/static/themes/DRRPP/img/list_img.png" % appname,
                         _id="list_img"),
                     _href=URL(c="project", f="project", args=["list"]),
                     _title="Project List")

        matrix_img = A(IMG(_src="/%s/static/themes/DRRPP/img/matrix_img.png" % appname,
                           _id="matrix_img"),
                       _href=URL(c="project", f="project", args=["matrix"]),
                       _title="Project Matrix Report")

        map_img = A(IMG(_src="/%s/static/themes/DRRPP/img/map_img.png" % appname,
                        _id="map_img"),
                    _href=URL( f="project", args=["map"]),
                    _title="Project Map")

        graph_img = A(IMG(_src="/%s/static/themes/DRRPP/img/graph_img.png" % appname,
                          _id="graph_img"),
                      _href=URL(c="project", f="project", args=["graphs"]),
                      _title="Project Graph")

        add_pipeline_project_link = URL(c="project",
                                        f="project",
                                        args=["create"],
                                        vars=dict(set_status_id = "1"))
        add_current_project_link = URL(c="project",
                                       f="project",
                                       args=["create"],
                                       vars=dict(set_status_id = "2"))
        add_completed_project_link = URL(c="project",
                                         f="project",
                                         args=["create"],
                                         vars=dict(set_status_id = "3"))
        add_offline_project_link = URL(c="static",
                                       f="DRR_Project_Portal_New_Project_Form.doc")

        add_framework_link = URL(c="project",
                                 f="framework",
                                 args=["create"])

        project_captions = {
            1:"DRR projects which will be being implemented in the future, and for which funding has been secured in the Asia and Pacific region.",
            2:"DRR projects which are currently being implemented in one or more country in the Asia and Pacific region.",
            3:"DRR projects which have been completed and are no longer being implemented in the Asia and Pacific region."
            }
        framework_caption = "Frameworks, action plans, road maps, strategies, declarations, statements and action agendas on DRR or DRR related themes, which are documents or instruments for guiding stakeholders on DRR planning, programming and implementation."
        add_div = DIV(A(DIV("ADD ", SPAN("CURRENT", _class="white_text"), " PROJECT"),
                        _href=add_current_project_link,
                        _title=project_captions[2]),
                      A(DIV("ADD ", SPAN("PROPOSED", _class="white_text"), " PROJECT" ),
                        _href=add_pipeline_project_link,
                        _title=project_captions[1]),
                      A(DIV("ADD ", SPAN("COMPLETED", _class="white_text"), " PROJECT" ),
                        _href=add_completed_project_link,
                        _title=project_captions[3]),
                      A(DIV("ADD PROJECT OFFLINE" ),
                        _href=add_offline_project_link,
                        _title="Download a form to enter a DRR projects off-line and submit by Email"),
                      A(DIV("ADD ", SPAN("DRR FRAMEWORK", _class="white_text")),
                        _href=add_framework_link,
                        _title=framework_caption),
                      _id="add_div"
                     )

        why_box = DIV(H1("WHY THIS PORTAL?"),
                      UL("Share information on implementation of DRR: Who? What? Where?",
                         "Collectively identify gaps, improve planning and programming on DRR",
                         "Identify areas of cooperation on implementation of DRR"
                         ),
                      _id="why_box")

        what_box = DIV(H1("WHAT CAN WE GET FROM THIS PORTAL?"),
                       UL("List of completed and ongoing DRR projects - by country, hazards, themes, partners and donors.",
                          "List of planned/proposed projects - better planning of future projects.",
                          "Quick analysis - on number and types of completed and ongoing DRR projects",
                          "Generate customised graphs and maps.",
                          "Know more on the DRR frameworks/action plans guiding the region - identify priority areas for providing support and implementation.",
                          "List of organisations implementing DRR projects at regional level.",
                          "Archive of periodic meetings of regional DRR mechanisms."
                          ),
                       _id="what_box")

        how_help_box = DIV(H1("HOW WOULD THIS INFORMATION HELP?"),
                           H2("National Government"),
                           UL("Gain clarity on types of support that may be accessed from regional level and thus receive coherent regional assistance"),
                           H2("Organisation Implementing DRR Projects"),
                           UL("Plan better-knowing who does what, and where; Find partners and scale up implementation; and Learn from past and ongoing work of partners"),
                           H2("Donor Agencies"),
                           UL("Identify priorities to match your policy and programmatic imperatives; and minimise overlap; maximise resources"),
                           _id="how_help_box")

        how_start_box = DIV(H1("HOW DO WE GET STARTED?"),
                            UL("Add information on  current / proposed / completed DRR projects",
                               "Search for information - project list, project analysis, DRR frameworks",
                               "Log in to add and edit your data",
                               "Link to this portal from your organisation website"
                               ),
                            _id="how_start_box")

        help = A(DIV("USER MANUAL",
                     _id="help_div"),
                 _href=URL(c="static", f="DRR_Portal_User_Manual.pdf"),
                 _target="_blank"
                 )

        tour = A(DIV("VIDEO TOUR",
                     _id="tour_div"),
                 _href=URL(c="default", f="index", args="video"),
                 _target="_blank"
                 )

        db = current.db
        s3db = current.s3db
        table = s3db.project_project
        query = (table.deleted == False)
        #approved = & (table.approved == True)
        #current = & (table.status_id == 2)
        #proposed = & (table.status_id == 1)
        #completed = & (table.status_id == 1)
        projects = db(query).count()
        ftable = s3db.project_framework
        query = (ftable.deleted == False)
        #approved = & (table.approved == True)
        frameworks = db(query).count()
        stats = DIV(DIV("Currently the DRR Projects Portal has information on:"),
                    TABLE(TR(projects,
                             A("Projects",
                               _href=URL(c="project", f="project",
                                         args=["list"]))
                             ),
                          TR(TD(),
                             TABLE(TR(projects,
                                      A("Current Projects",
                                        _href=URL(c="project", f="project",
                                                  args=["list"],
                                                  vars={"status_id":2}))
                                     )
                                   )
                             ),
                          TR(TD(),
                             TABLE(TR(projects,
                                      A("Proposed Projects",
                                        _href=URL(c="project", f="project",
                                                  args=["list"],
                                                  vars={"status_id":1}))
                                     )
                                    )
                             ),
                          TR(TD(),
                             TABLE(TR(projects,
                                      A("Completed Projects",
                                        _href=URL(c="project", f="project",
                                                  args=["list"],
                                                  vars={"status_id":3}))
                                     )
                                    )
                             ),
                          TR(frameworks,
                             A("Frameworks",
                               _href=URL(c="project", f="framework"))
                            ),
                         ),
                    _id="stats_div")

        market = DIV(DIV(I("Under Development...")),
                     H2("DRR Project Marketplace"),
                     DIV("A platform to coordinate and collaborate on future DRR Projects."),
                     _id = "market_div")

        auth = current.auth
        _table_user = auth.settings.table_user
        _table_user.language.label = T("Language")
        _table_user.language.default = "en"
        _table_user.language.comment = DIV(_class="tooltip",
                                           _title=T("Language|The language to use for notifications."))
        #_table_user.language.requires = IS_IN_SET(s3_languages)
        languages = current.deployment_settings.get_L10n_languages()
        _table_user.language.represent = lambda opt: \
            languages.get(opt, current.messages.UNKNOWN_OPT)

        request.args = ["login"]
        login = auth()
        login[0][-1][1][0] = INPUT_BTN(_type = "submit",
                                      _value = T("Login"))

        return dict(title = T("Home"),
                    home_img = home_img,
                    add_div = add_div,
                    login = login,
                    why_box = why_box,
                    home_page_img = home_page_img,
                    what_box = what_box,
                    how_help_box = how_help_box,
                    home_map_img = home_map_img,
                    how_start_box = how_start_box,
                    tour = tour,
                    help = help,
                    stats = stats,
                    market = market,
                    list_img = list_img,
                    matrix_img = matrix_img,
                    map_img = map_img,
                    graph_img = graph_img,
                    )


# =============================================================================
class register():
    """ Custom Registration Page """

    def __call__(self):

        request = current.request
        response = current.response

        view = path.join(request.folder, "private", "templates",
                         "DRRPP", "views", "register.html")
        try:
            # Pass view as file not str to work in compiled mode
            response.view = open(view, "rb")
        except IOError:
            from gluon.http import HTTP
            raise HTTP("404", "Unable to open Custom View: %s" % view)

        T = current.T
        auth = current.auth
        _settings = auth.settings

        # Default the profile language to the one currently active
        table = _settings.table_user
        table.language.default = T.accepted_language

        # Combo box for Organisation
        table.organisation_id.widget = S3OrganisationAutocompleteWidget(new_items=True)
        table.organisation_id.requires = IS_COMBO_BOX("org_organisation",
                                                      current.s3db.org_organisation_id.attr.requires),

        # Custom onaccept to process custom fields
        _settings.register_onaccept = register_onaccept

        # Build the registration form
        form = auth()
        form.attributes["_id"] = "regform"

        # Set the formstyle
        _form = form[0]
        _form[-1] = TR(TD(_class="w2p_fl"),
                       TD(_class="w2p_fc"),
                       TD(INPUT_BTN(_type="submit",
                                    _value=T("Register")),
                          _class="w2p_fw"),
                       _id="submit_record_row"
                       )
        _form[0] = TR(TD(SPAN(" *", _class="req"),
                         _class="w2p_fl"),
                      TD(LABEL(DIV("%s: " % T("First Name")),
                               _id="auth_user_first_name__label",
                               _for="auth_user_first_name"),
                         _class="w2p_fc"),
                      TD(INPUT(_id="auth_user_first_name",
                               _class="string",
                               _type="text",
                               _name="first_name",
                               _size="62"),
                         _class="w2p_fw"),
                      _id="auth_user_first_name_row"
                      )
        _form[1] = TR(TD(SPAN(" *", _class="req"),
                         _class="w2p_fl"),
                      TD(LABEL(DIV("%s: " % T("Last Name")),
                               _id="auth_user_last_name__label",
                               _for="auth_user_last_name"),
                         _class="w2p_fc"),
                      TD(INPUT(_id="auth_user_last_name",
                               _class="string",
                               _type="text",
                               _name="last_name",
                               _size="62"),
                         _class="w2p_fw"),
                      _id="auth_user_last_name_row"
                      )
        _form[2] = TR(TD(_class="w2p_fl"),
                      TD(LABEL(DIV("%s: " % T("Organization")),
                               _id="auth_user_organisation_id__label",
                               _for="auth_user_organisation_id"),
                         _class="w2p_fc"),
                      TD(form.custom.widget.organisation_id,
                         _class="w2p_fw"),
                      _id="auth_user_organisation_id_row"
                      )
        _form[3] = TR(TD(SPAN(" *", _class="req"),
                         _class="w2p_fl"),
                      TD(LABEL(DIV("%s: " % T("E-Mail")),
                               _id="auth_user_email__label",
                               _for="auth_user_email"),
                         _class="w2p_fc"),
                      TD(INPUT(_id="auth_user_email",
                               _class="string",
                               _type="text",
                               _name="email",
                               _size="62"),
                         _class="w2p_fw"),
                      _id="auth_user_email_row"
                      )
        _form[4] = TR(TD(SPAN(" *", _class="req"),
                         _class="w2p_fl"),
                      TD(LABEL(DIV("%s: " % T("Password")),
                               _id="auth_user_password__label",
                               _for="auth_user_password"),
                         _class="w2p_fc"),
                      TD(INPUT(_id="auth_user_password",
                               _type="password",
                               _name="password",
                               _class="password",
                               ),
                         _class="w2p_fw"),
                      _id="auth_user_password_row"
                      )
        _form[5] = TR(TD(SPAN(" *", _class="req"),
                         _class="w2p_fl"),
                      TD(LABEL(DIV("%s: " % T("Verify Password")),
                               _id="auth_user_password_two__label",
                               _for="auth_user_password_two"),
                         _class="w2p_fc"),
                      TD(INPUT(_id="auth_user_password_two",
                               _type="password",
                               _name="password_two",
                               _class="password",
                               ),
                         _class="w2p_fw"),
                      _id="auth_user_password_two_row"
                      )

        # Add custom fields
        append = _form[2].append
        append(
                TR(TD(SPAN(" *", _class="req"),
                      _class="w2p_fl"),
                   TD(LABEL(DIV("%s: " % T("Role")),
                            _id="auth_user_position__label",
                            _for="auth_user_position"),
                      _class="w2p_fc"),
                   TD(SELECT(OPTION(_value=""),
                             OPTION(T("Practitioner"),
                                    _value="1"),
                             OPTION(T("Consultant"),
                                    _value="2"),
                             OPTION(T("Researcher"),
                                    _value="3"),
                             OPTION(T("Academic"),
                                    _value="4"),
                             OPTION(T("Student"),
                                    _value="5"),
                             _name="position",
                             _id="auth_user_position",
                             _class="integer"
                             ),
                      _class="w2p_fw"),
                   _id="auth_user_position_row"
                   )
            )
        append(
                TR(TD(SPAN(" *", _class="req"),
                      DIV(_rel="If you do not specify an organisation, please enter your reason for using the DRR Project Portal.",
                          _class="labeltip"),
                      _class="w2p_fl"),
                   TD(LABEL(DIV("%s: " % T("Reason")),
                            _id="auth_user_reason__label",
                            _for="auth_user_reason"),
                      _class="w2p_fc"),
                   TD(TEXTAREA(_id="auth_user_reason",
                               _class="text",
                               _name="reason",
                               _rows="10",
                               _cols="50",
                               ),
                      _class="w2p_fw"),
                   _id="auth_user_reason_row"
                   )
            )

        # Add client-side validation
        s3 = response.s3
        appname = request.application
        if s3.debug:
            s3.scripts.append("/%s/static/scripts/jquery.pstrength.1.3.js" % appname)
            s3.scripts.append("/%s/static/scripts/jquery.validate.js" % appname)
        else:
            s3.scripts.append("/%s/static/scripts/jquery.pstrength.1.3.min.js" % appname)
            s3.scripts.append("/%s/static/scripts/jquery.validate.min.js" % appname)
        s3.jquery_ready.append("".join(('''
$('#regform').validate({
 errorClass:'req',
 rules:{
  first_name:{
   required:true
  },
  last_name:{
   required:true
  },
  position:{
   required:true,
  },
  reason:{
   required:true,
  },
  email:{
   required:true,
   email:true
  },
  password:{
   required:true
  },
  password_two:{
   required:true,
   equalTo:'.password:first'
  }
 },
 messages:{
  first_name:"''', str(T("Enter your first name")), '''",
  last_name:"''', str(T("Enter your last name")), '''",
  position:"''', str(T("Select your role")), '''",
  reason:"''', str(T("Enter a reason")), '''",
  password:{
   required:"''', str(T("Provide a password")), '''"
  },
  password_two:{
   required:"''', str(T("Repeat your password")), '''",
   equalTo:"''', str(T("Enter the same password as above")), '''"
  },
  email:{
   required:"''', str(T("Please enter a valid email address")), '''",
   email:"''', str(T("Please enter a valid email address")), '''"
  }
 },
 errorPlacement:function(error,element){
  error.appendTo(element.parent())
 },
 submitHandler:function(form){
  form.submit()
 }
})
$('.password:first').pstrength({minchar:''', str(_settings.password_min_length), ''',minchar_label:"''', str(T("The minimum number of characters is ")), '''"})
$('.labeltip').cluetip({activation:'hover',position:'mouse',sticky:false,showTitle:false,local:true})''')))

        response.title = T("DRRPP - Register")

        return dict(form=form)

# -----------------------------------------------------------------------------
def register_onaccept(form):
    """ Tasks to be performed after a new user registers """

    # Add newly-registered users to Person Registry, add 'Authenticated' role
    # If Organisation is provided, then add HRM record
    person_id = current.auth.s3_register(form)

    # Process Custom Fields
    vars = form.request_vars
    position = vars.get("position", "")
    reason = vars.get("reason", "")
    id = form.vars.id
    db = current.db
    table = db.auth_user
    db(table.id==form.vars.id).update(comments = "%s | %s" % (position, reason))

# =============================================================================
class contact():
    """ Contact Form """

    def __call__(self):

        request = current.request
        response = current.response

        view = path.join(request.folder, "private", "templates",
                         "DRRPP", "views", "contact.html")
        try:
            # Pass view as file not str to work in compiled mode
            response.view = open(view, "rb")
        except IOError:
            from gluon.http import HTTP
            raise HTTP("404", "Unable to open Custom View: %s" % view)

        if request.env.request_method == "POST":
            # Processs Form
            vars = request.post_vars
            result = current.msg.send_email(
                    #to=current.deployment_settings.get_mail_approver(),
                    to="admin@drrprojects.net",
                    subject=vars.subject,
                    message=vars.message,
                    reply_to=vars.address,
                )
            if result:
                response.confirmation = "Thankyou for your message - we'll be in touch shortly"

        #T = current.T

        form = DIV(
                H1("Contact Us"),
                P("You can leave a message using the contact form below."),
                FORM(TABLE(
                        TR(LABEL("Your name:",
                              SPAN(" *", _class="req"),
                              _for="name")),
                        TR(INPUT(_name="name", _type="text", _size=62, _maxlength="255")),
                        TR(LABEL("Your e-mail address:",
                              SPAN(" *", _class="req"),
                              _for="address")),
                        TR(INPUT(_name="address", _type="text", _size=62, _maxlength="255")),
                        TR(LABEL("Subject:",
                              SPAN(" *", _class="req"),
                              _for="subject")),
                        TR(INPUT(_name="subject", _type="text", _size=62, _maxlength="255")),
                        TR(LABEL("Message:",
                              SPAN(" *", _class="req"),
                              _for="name")),
                        TR(TEXTAREA(_name="message", _class="resizable", _rows=5, _cols=62)),
                        TR(INPUT(_type="submit", _value="Send e-mail")),
                        ),
                    _id="mailform"
                    )
                )
        s3 = response.s3
        if s3.cdn:
            if s3.debug:
                s3.scripts.append("http://ajax.aspnetcdn.com/ajax/jquery.validate/1.9/jquery.validate.js")
            else:
                s3.scripts.append("http://ajax.aspnetcdn.com/ajax/jquery.validate/1.9/jquery.validate.min.js")

        else:
            if s3.debug:
                s3.scripts.append("/%s/static/scripts/jquery.validate.js" % request.application)
            else:
                s3.scripts.append("/%s/static/scripts/jquery.validate.min.js" % request.application)
        s3.jquery_ready.append(
'''$('#mailform').validate({
 errorClass:'req',
 rules:{
  name:{
   required:true
  },
  subject:{
   required:true
  },
  message:{
   required:true
  },
  name:{
   required:true
  },
  address: {
   required:true,
   email:true
  }
 },
 messages:{
  name:"Enter your name",
  subject:"Enter a subject",
  message:"Enter a message",
  address:{
   required:"Please enter a valid email address",
   email:"Please enter a valid email address"
  }
 },
 errorPlacement:function(error,element){
  error.appendTo(element.parents('tr').prev().children())
 },
 submitHandler:function(form){
  form.submit()
 }
})''')

        response.title = "Contact | DRR Project Portal"
        return dict(form=form)


# =============================================================================
class test2():
    """
    """

    def __call__(self):
        settings = current.deployment_settings
        response = current.response
        request = current.request
        s3db = current.s3db
        db = current.db
        T = current.T

        view = path.join(request.folder, "private", "templates",
                         "DRRPP", "views", "project_create_2.html")
        try:
            # Pass view as file not str to work in compiled mode
            response.view = open(view, "rb")
        except IOError:
            from gluon.http import HTTP
            raise HTTP("404", "Unable to open Custom View: %s" % view)

        # project form with custom fields included
        project_form = SQLFORM.factory(
            s3db.project_project.name,
            s3db.project_project.code,
            s3db.project_project.status,
            s3db.project_project.start_date,
            s3db.project_project.end_date,
            s3db.project_project.countries_id,
            s3db.project_project.multi_hazard_id,
            s3db.project_project.multi_theme_id,
            s3db.project_project.objectives,
            Field(
                "activities",
                "text",
                label=T("Activities")
            ),
            # outputs
            s3db.project_project.hfa,
            #s3db.project_project.rfa,
            Field(
                "lead_organisation",
                label=T("Lead Organisation")
            ),
            # partner organisations
            # donors
            s3db.project_project.budget,
            s3db.project_project.currency,
            Field(
                "contact_name",
                label=T("Focal Person")
            ),
            Field(
                "contact_organisation",
                label=T("Organisation")
            ),
            Field(
                "contact_email",
                label=T("Email")
            ),
            # files
            # links
            s3db.project_project.comments,
            Field(
                "parent_project",
                label=T("Main Project"),
                comment=T("If this project is implemented as part of a \
                           programme or another poject, select it here.")
            ),
        )

        # formsets
        formsets = {}

        formsets["outputs"] = SQLFORM.factory(
            Field(
                "output",
                label=T("Output")
            ),
            Field(
                "status",
                label=T("Status")
            )
        )

        import copy
        formsets["partners"] = []
        total_forms = int(request.post_vars.get("partners_TOTAL_FORMS", 1))
        for x in range(0, total_forms):
            prefix = "partners_%s_" % x

            test = ["test", "blewrg", "raw"]

            form = SQLFORM.factory(
                    Field(
                        "%sorganisation_id" % prefix,
                        "string",
                        label=T("Organisation"),
                        #~ requires=[IS_IN_SET(
                            #~ db, "org_organisation.id",
                            #~ org_organisation_represent,
                            #~ orderby="org_organisation.name",
                            #~ sort=True)]
                        requires=IS_IN_DB(db, db.org_organisation.id, zero="huh?")
                    ),
                    Field(
                        "%scomments" % prefix,
                        label=T("Comments"),
                    ),
                    table_name="id"
                )

            if request.post_vars:
                if any(request.post_vars[field] for field in form.fields):
                    #print request.post_vars
                    #post = copy.deepcopy(request.post_vars)
                    post = dict([(key, value) for key, value in request.post_vars.items()])
                    print "post: %s" % post

                    # if organisation is a string, do the organisation lookup
                    try:
                        post["organisation_id"] = int(request.post_vars["%sorganisation_id" % prefix])
                    except ValueError:
                        post["organisation_id"] = s3db.org_organisation.insert(request.post_vars["%sorganisation_id" % prefix])

                    if form.accepts(post, formname=None, keepvalues=True):
                        print "%s: accepted" % prefix

                        # create new dict to pass to insert
                        clean_vars = dict([(field.replace(prefix, ""), value) for field, value in request.post_vars.items() if field.startswith(prefix)])
                        clean_vars["role"] = "2" # partner
                        print "clean_vars: %s" % clean_vars

                        table_form = SQLFORM(s3db.project_organisation)

                        if table_form.accepts(clean_vars, formname=None):
                            print "Table form accepted"
                            # insert into database
                        elif table_form.errors:
                            print table_form.errors
                    elif form.errors:
                        # form has errors
                        project_form.errors.update(form.errors)
                    else:
                        # do nothing
                        pass
                else:
                    # all fields are blank
                    continue

            formsets["partners"].append(form)




        formsets["donors"] = [SQLFORM.factory(
            Field(
                "donor_agency",
                label=T("Agency")
            ),
            Field(
                "donor_amount",
                label=T("Amount"),
                length=16
            ),
            s3_currency("donor_currency", writable=True)
        )]

        formsets["files"] = SQLFORM.factory(
            Field(
                "files_file",
                label=T("File"),
                type="upload"
            ),
            Field(
                "files_comment",
                label=T("Comment")
            )
        )

        formsets["links"] = SQLFORM.factory(
            Field(
                "links_url",
                label=T("URL")
            ),
            Field(
                "links_comment",
                label=T("Comment")
            )
        )

        return dict(project_form=project_form, formsets=formsets)


# =============================================================================
class test():
    """
    """

    def __call__(self):
        response = current.response
        request = current.request
        s3db = current.s3db
        db = current.db
        T = current.T

        view = path.join(request.folder, "private", "templates",
                         "DRRPP", "views", "project_create.html")
        try:
            # Pass view as file not str to work in compiled mode
            response.view = open(view, "rb")
        except IOError:
            from gluon.http import HTTP
            raise HTTP("404", "Unable to open Custom View: %s" % view)

        main_form = forms.project_form()

        formsets = {}
        fs = [
            ("project_outputs", forms.project_outputs_form),
            ("partner_organisations", forms.partner_organisations_form),
            ("donor_organisations", forms.donor_organisations_form),
            ("project_files", forms.project_files_form),
            ("project_links", forms.project_links_form),
        ]

        for name, form_function in fs:
            quantity = int(request.vars.get("%s_TOTAL_FORMS" % name, 1))
            formsets[name] = forms.formset_factory(name, form_function, quantity)

        if request.post_vars:
            clean_vars = dict([(key, value) for key, value in request.post_vars.items() if value])
            print clean_vars

            if main_form.accepts(clean_vars, keepvalues=True, formname=None):
                #project_id = s3db.project_project.insert(**s3db.project_project._filter_fields(main_form.vars))

                # insert the lead organisation
                #s3db.project_organisation.insert(organisation_id=project_form.vars.lead_organisation, project_id=project_id, role=1)

                response.flash = "Form project_form accepted"
                #redirect(URL(c="project", f="project", args=project_id))
            elif main_form.errors:
                print "Has errors: %s" % main_form.errors
            else:
                print "no processing"

            for name, form_func in fs:
                for index, form in enumerate(formsets[name]):
                    prefix = "%s_%s_" % (name, index)
                    #formset_vars = dict([(key.replace(prefix, ""), value) for key, value in clean_vars.items() if key.startswith(prefix)])
                    formset_vars = Storage([(key, value) for key, value in clean_vars.items() if key.startswith(prefix)])

                    for field, value in formset_vars.items():
                        field = field.replace(prefix, "")
                        formset_vars[field] = value

                    print "formset_vars %s: %s" % (prefix, formset_vars)

                    if formset_vars:
                        if form.accepts(formset_vars, keepvalues=True, formname=None):
                            print "formset form %s accepted" % name
                            try:
                                # if project_id is not None
                                # save to database
                                pass
                            except KeyError:
                                pass
                        elif form.errors:
                            print "formset form errors: %s" % form.errors
                            for field, error in form.errors.items():
                                form.errors["%s%s" % (prefix, field)] = error
                        else:
                            # ignored
                            pass
                        print "form.vars: %s" % form.vars

        response.title = "Add Project | DRR Project Portal"
        return dict(project_form=main_form, formsets=formsets)


# =============================================================================
class organisations():
    """
    """

    def __call__(self):

        from gluon.storage import Storage
        from s3 import S3FieldSelector

        T = current.T
        request = current.request
        response = current.response

        response.title = "DRR Projects Portal - Regional Organizations"
        view = path.join(request.folder, "private", "templates",
                         "DRRPP", "views", "organisations.html")
        try:
            # Pass view as file not str to work in compiled mode
            response.view = open(view, "rb")
        except IOError:
            from gluon.http import HTTP
            raise HTTP("404", "Unable to open Custom View: %s" % view)

        tables = []
        table = request.vars.get("table", None)

        # URL format breaks the REST controller conventions
        request.args.pop()

        # Regional Organisations
        s3request, field_list = self._regional()
        tables.append(self._table("regional", s3request.resource, field_list))

        # Groups
        s3request, field_list = self._groups()
        tables.append(self._table("groups", s3request.resource, field_list))

        return dict(tables=tables,
                    appname=request.application)

    # -------------------------------------------------------------------------
    @staticmethod
    def _regional():
        """
        """

        from s3 import S3FieldSelector
        T = current.T

        s3request = current.manager.parse_request("org",
                                                  "organisation",
                                                  extension="aadata")
        f = (S3FieldSelector("organisation_type_id$name").anyof(["Regional Organisation"]))
        s3request.resource.add_filter(f)

        field_list = [
            "id",
            "name",
            "acronym",
            (T("Type"), "organisation_type_id"),
            "website",
            "region",
            "year",
            (T("Notes"), "comments")
        ]
        return (s3request, field_list)

    # -------------------------------------------------------------------------
    @staticmethod
    def _groups():
        """
        """

        from s3 import S3FieldSelector
        T = current.T

        s3request = current.manager.parse_request("org",
                                                  "organisation",
                                                  extension="aadata")
        f = (S3FieldSelector("organisation_type_id$name").anyof(["Forum"]))
        s3request.resource.add_filter(f)

        field_list = [
            "id",
            "name",
            "acronym",
            (T("Type"), "organisation_type_id"),
            "year",
            "address",
            (T("Notes"), "comments")
        ]
        return (s3request, field_list)

    # -------------------------------------------------------------------------
    @staticmethod
    def _table(name, resource, field_list, limit=10, orderby="name"):
        """
        """

        from s3 import S3FieldSelector
        T = current.T

        fields = []
        cols = []
        for field_name in field_list:
            if isinstance(field_name, tuple):
                field_label = field_name[0]
                field_name = field_name[1]
            else:
                field_label = None

            fs = S3FieldSelector(field_name)
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
                                 start=None,
                                 limit=None,
                                 orderby=orderby,
                                 as_page=True)

        if rows is None:
            rows = []

        options = json.dumps({
            "iDisplayLength": limit,
            "iDeferLoading": len(resource.load()),
            "bProcessing": True,
            #"bServerSide": True,
            #"sAjaxSource": "/%s/default/index/organisations/?table=%s" % (current.request.application, name),
            "aoColumnDefs": [
                {
                    "bVisible": False,
                    "aTargets": [0]
                }
            ],
            "aoColumns": [{"sName": col["name"]} for col in cols],
            "sDom": "frltpi",
        })

        table = Storage(
            cols=cols,
            rows=rows,
            options=options,
            classes="dataTable display"
        )

        return table

# END =========================================================================
