# -*- coding: utf-8 -*-

"""
    Messaging Module - Controllers
"""

module = request.controller
resourcename = request.function

if not deployment_settings.has_module(module):
    raise HTTP(404, body="Module disabled: %s" % module)

# -----------------------------------------------------------------------------
def index():
    """ Module's Home Page """

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name
    return dict(module_name=module_name)

# =============================================================================
def compose():
    """ Compose a Message which can be sent to a pentity via a number of different communications channels """

    return msg.compose()

# -----------------------------------------------------------------------------
# Send Outbound Messages - to be called via cron
# -----------------------------------------------------------------------------
def process_email():
    """ Controller for Email processing - to be called via cron """

    msg.process_outbox(contact_method="EMAIL")
    return

# -----------------------------------------------------------------------------
def process_sms():
    """ Controller for SMS processing - to be called via cron """

    msg.process_outbox(contact_method="SMS")
    return

# -----------------------------------------------------------------------------
def process_twitter():
    """ Controller for Twitter message processing - to be called via cron """

    msg.process_outbox(contact_method="TWITTER")
    return

# =============================================================================
def outbox():
    """ View the contents of the Outbox """

    if not auth.s3_logged_in():
        session.error = T("Requires Login!")
        redirect(URL(c="default", f="user", args="login"))

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    table.message_id.label = T("Message")
    table.message_id.writable = False
    table.pe_id.readable = True
    table.pe_id.label = T("Recipient")

    # Subject works for Email but not SMS
    table.message_id.represent = lambda id: db(db.msg_log.id == id).select(db.msg_log.message, limitby=(0, 1)).first().message
    table.pe_id.represent = lambda id: s3db.pr_pentity_represent(id, default_label="")

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
        title_list=T("View Outbox"),
        title_update=T("Edit Message"),
        label_list_button=T("View Outbox"),
        label_delete_button=T("Delete Message"),
        msg_record_modified=T("Message updated"),
        msg_record_deleted=T("Message deleted"),
        msg_list_empty=T("No Messages currently in Outbox")
    )

    add_btn = A(T("Compose"),
                _class="action-btn",
                _href=URL(f="compose")
                )

    s3db.configure(tablename, listadd=False)
    return s3_rest_controller(module, resourcename, add_btn=add_btn)

# =============================================================================
def log():
    """
        RESTful CRUD controller for the Master Message Log
        - all Inbound & Outbound Messages go here

        @ToDo: Field Labels for i18n
    """

    if not auth.s3_logged_in():
        session.error = T("Requires Login!")
        redirect(URL(c="default", f="user", args="login"))

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    # CRUD Strings
    ADD_MESSAGE = T("Add Message")
    s3.crud_strings[tablename] = Storage(
        title_create=ADD_MESSAGE,
        title_display=T("Message Details"),
        title_list=T("Messages"),
        title_update=T("Edit message"),
        title_search=T("Search messages"),
        subtitle_create=T("Send new message"),
        label_list_button=T("List Messages"),
        label_create_button=ADD_MESSAGE,
        msg_record_created=T("Message added"),
        msg_record_modified=T("Message updated"),
        msg_record_deleted=T("Message deleted"),
        msg_list_empty=T("No messages in the system"))

    s3db.configure(tablename, listadd=False)
    return s3_rest_controller()

# =============================================================================
def tropo():
    """
        Receive a JSON POST from the Tropo WebAPI

        @see: https://www.tropo.com/docs/webapi/newhowitworks.htm
    """

    # Stored in modules/tropo.py
    from tropo import Tropo, Session

    try:
        s = Session(request.body.read())
        t = Tropo()
        # This is their service contacting us, so parse their request
        try:
            row_id = s.parameters["row_id"]
            # This is an Outbound message which we've requested Tropo to send for us
            table = s3db.msg_tropo_scratch
            query = (table.row_id == row_id)
            row = db(query).select().first()
            # Send the message
            #t.message(say_obj={"say":{"value":row.message}},to=row.recipient,network=row.network)
            t.call(to=row.recipient, network=row.network)
            t.say(row.message)
            # Update status to sent in Outbox
            outbox = s3db.msg_outbox
            db(outbox.id == row.row_id).update(status=2)
            # Set message log to actioned
            log = s3db.msg_log
            db(log.id == row.message_id).update(actioned=True)
            # Clear the Scratchpad
            db(query).delete()
            return t.RenderJson()
        except:
            # This is an Inbound message
            try:
                message = s.initialText
                # This is an SMS/IM
                # Place it in the InBox
                uuid = s.id
                recipient = s.to["id"]
                try:
                    fromaddress = s.fromaddress["id"]
                except:
                    # SyntaxError: s.from => invalid syntax (why!?)
                    fromaddress = ""
                s3db.msg_log.insert(uuid=uuid, fromaddress=fromaddress,
                                    recipient=recipient, message=message,
                                    inbound=True)
                # Send the message to the parser
                reply = msg.parse_message(message)
                t.say([reply])
                return t.RenderJson()
            except:
                # This is a Voice call
                # - we can't handle these yet
                raise HTTP(501)
    except:
        # GET request or some random POST
        pass

# =============================================================================
def twitter_search():
    """ Controller to modify Twitter search queries """

    return s3_rest_controller()

# -----------------------------------------------------------------------------
def twitter_search_results():
    """ Controller to retrieve tweets for user saved search queries - to be called via cron. Currently in real time also. """

    # Update results
    result = msg.receive_subscribed_tweets()

    if not result:
        session.error = T("Need to configure Twitter Authentication")
        redirect(URL(f="twitter_settings", args=[1, "update"]))

    return s3_rest_controller()

# =============================================================================
@auth.s3_requires_membership(1)
def setting():
    """ SMS settings for the messaging framework """

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]
    table.outgoing_sms_handler.label = T("Outgoing SMS handler")
    table.outgoing_sms_handler.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Outgoing SMS Handler"),
                          T("Selects what type of gateway to use for outbound SMS"))))
    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
        title_update=T("Edit SMS Settings"),
        msg_record_modified=T("SMS settings updated")
    )

    def prep(r):
        if r.http == "POST":
            # Go to the details page for the chosen SMS Gateway
            outgoing_sms_handler = request.post_vars.get("outgoing_sms_handler",
                                                         None)
            if outgoing_sms_handler == "WEB_API":
                s3db.configure(tablename,
                                update_next=URL(f="api_settings",
                                                  args=[1, "update"]))
            elif outgoing_sms_handler == "SMTP":
                s3db.configure(tablename,
                                update_next=URL(f="smtp_to_sms_settings",
                                                  args=[1, "update"]))
            elif outgoing_sms_handler == "MODEM":
                s3db.configure(tablename,
                                update_next=URL(f="modem_settings",
                                                  args=[1, "update"]))
            elif outgoing_sms_handler == "TROPO":
                s3db.configure(tablename,
                                update_next=URL(f="tropo_settings",
                                                  args=[1, "update"]))
            else:
                s3db.configure(tablename,
                                update_next=URL(args=[1, "update"]))
        return True
    s3.prep = prep

    s3db.configure(tablename,
                    deletable=False,
                    listadd=False)
    #response.menu_options = admin_menu_options
    return s3_rest_controller()

# -----------------------------------------------------------------------------
def inbound_email_settings():
    """
        RESTful CRUD controller for email settings
            - appears in the administration menu
    """

    if not auth.s3_has_role(ADMIN):
        session.error = UNAUTHORISED
        redirect(URL(f="index"))

    tablename = "msg_inbound_email_settings"
    table = s3db[tablename]

    table.server.label = T("Server")
    table.protocol.label = T("Protocol")
    table.use_ssl.label = "SSL"
    table.port.label = T("Port")
    table.username.label = T("Username")
    table.password.label = T("Password")
    table.delete_from_server.label = T("Delete from Server?")
    table.port.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Port"),
                          T("For POP-3 this is usually 110 (995 for SSL), for IMAP this is usually 143 (993 for IMAP)."))))
    table.delete_from_server.comment = DIV(DIV(_class="tooltip",
            _title="%s|%s" % (T("Delete"),
                              T("If this is set to True then mails will be deleted from the server after downloading."))))

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
    title_display=T("Email Setting Details"),
    title_list=T("Email Settings"),
    title_create=T("Add Email Settings"),
    title_update=T("Edit Email Settings"),
    title_search=T("Search Email Settings"),
    label_list_button=T("View Email Settings"),
    label_create_button=T("Add Email Settings"),
    msg_record_created=T("Setting added"),
    msg_record_deleted=T("Email Setting deleted"),
    msg_list_empty=T("No Settings currently defined"),
    msg_record_modified=T("Email settings updated")
        )

    #response.menu_options = admin_menu_options
    s3db.configure(tablename, listadd=True, deletable=True)

    def postp(r, output):
        wtable = s3db.msg_workflow
        stable = s3db.scheduler_task
        mtable = r.table

        s3_action_buttons(r)
        query = (stable.enabled == False)
        records = db(query).select()
        rows = []
        for record in records:
            if "username" in record.vars:
                r = record.vars.split("\"username\":")[1]
                s = r.split("}")[0]
                s = s.split("\"")[1].split("\"")[0]

                record1 = db(mtable.username == s).select(mtable.id)
                if record1:
                    for rec in record1:
                        rows += [rec]

        restrict_e = [str(row.id) for row in rows]

        query = (stable.enabled == True)
        records = db(query).select()
        rows = []
        for record in records:
            if "username" in record.vars:
                r = record.vars.split("\"username\":")[1]
                s = r.split("}")[0]
                s = s.split("\"")[1].split("\"")[0]

                record1 = db(mtable.username == s).select(mtable.id)
                if record1:
                    for rec in record1:
                        rows += [rec]

        restrict_d = [str(row.id) for row in rows]

        rows = []
        records = db(stable.id > 0).select()
        tasks = [record.vars for record in records]
        sources = []
        for task in tasks:
            if "username" in task:
                u = task.split("\"username\":")[1]
                v = u.split(",")[0]
                v = v.split("\"")[1]
                sources += [v]

        msettings = db(mtable.deleted == False).select(mtable.ALL)
        for msetting in msettings :
            if msetting.username:
                if (msetting.username not in sources):
                    if msetting:
                        rows += [msetting]

        restrict_a = [str(row.id) for row in rows]

        s3.actions = \
        s3.actions + [
                       dict(label=str(T("Enable")),
                            _class="action-btn",
                            url=URL(f="enable_email",
                                    args="[id]"),
                            restrict=restrict_e)
                       ]
        s3.actions.append(dict(label=str(T("Disable")),
                               _class="action-btn",
                               url=URL(f="disable_email",
                                         args="[id]"),
                               restrict=restrict_d)
                          )
        s3.actions.append(dict(label=str(T("Activate")),
                               _class="action-btn",
                               url=URL(f="schedule_email",
                                         args="[id]"),
                               restrict=restrict_a)
                          )
        return output
    s3.postp = postp

    return s3_rest_controller()

# -----------------------------------------------------------------------------
def twilio_inbound_settings():
    """
        RESTful CRUD controller for twilio sms settings
            - appears in the administration menu
    """

    if not auth.s3_has_role(ADMIN):
        session.error = UNAUTHORISED
        redirect(URL(f="index"))

    tablename = "msg_twilio_inbound_settings"
    table = s3db[tablename]

    table.account_name.label = T("Account Name")
    table.account_name.comment = DIV(DIV(_class="tooltip",
            _title="%s|%s" % (T("Account Name"),
                              T("Identifier Name for your Twilio Account."))))

    table.url.label = T("URL")
    table.url.comment = DIV(DIV(_class="tooltip",
            _title="%s|%s" % (T("URL"),
                              T("URL for the twilio API."))))

    table.account_sid.label = "Account SID"
    table.auth_token.label = T("AUTH TOKEN")

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
    title_display=T("Twilio Setting Details"),
    title_list=T("Twilio Settings"),
    title_create=T("Add Twilio Settings"),
    title_update=T("Edit Twilio Settings"),
    title_search=T("Search Twilio Settings"),
    label_list_button=T("View Twilio Settings"),
    label_create_button=T("Add Twilio Settings"),
    msg_record_created=T("Twilio Setting added"),
    msg_record_deleted=T("Twilio Setting deleted"),
    msg_list_empty=T("No Twilio Settings currently defined"),
    msg_record_modified=T("Twilio settings updated")
        )

    #response.menu_options = admin_menu_options
    s3db.configure(tablename, listadd=True, deletable=True)

    def postp(r, output):

        stable = s3db.scheduler_task
        ttable = r.table

        s3_action_buttons(r)
        query = (stable.enabled == False)
        records = db(query).select()
        rows = []
        for record in records:
            if "account" in record.vars:
                r = record.vars.split("\"account\":")[1]
                s = r.split("}")[0]
                s = s.split("\"")[1].split("\"")[0]

                record1 = db(ttable.account_name == s).select(ttable.id)
                if record1:
                    for rec in record1:
                        rows += [rec]

        restrict_e = [str(row.id) for row in rows]

        query = (stable.enabled == True)
        records = db(query).select()
        rows = []
        for record in records:
            if "account" in record.vars:
                r = record.vars.split("\"account\":")[1]
                s = r.split("}")[0]
                s = s.split("\"")[1].split("\"")[0]

                record1 = db(ttable.account_name == s).select(ttable.id)
                if record1:
                    for rec in record1:
                        rows += [rec]

        restrict_d = [str(row.id) for row in rows]

        rows = []
        records = db(stable.id > 0).select()
        tasks = [record.vars for record in records]
        sources = []
        for task in tasks:
            if "account" in task:
                u = task.split("\"account\":")[1]
                v = u.split(",")[0]
                v = v.split("\"")[1]
                sources += [v]

        tsettings = db(ttable.deleted == False).select(ttable.ALL)
        for tsetting in tsettings :
            if tsetting.account_name:
                if (tsetting.account_name not in sources):
                    if tsetting:
                        rows += [tsetting]

        restrict_a = [str(row.id) for row in rows]

        s3.actions = \
        s3.actions + [
                       dict(label=str(T("Enable")),
                            _class="action-btn",
                            url=URL(f="enable_twilio_sms",
                                    args="[id]"),
                            restrict=restrict_e)
                       ]
        s3.actions.append(dict(label=str(T("Disable")),
                               _class="action-btn",
                               url=URL(f="disable_twilio_sms",
                                         args="[id]"),
                               restrict=restrict_d)
                          )
        s3.actions.append(dict(label=str(T("Activate")),
                               _class="action-btn",
                               url=URL(f="schedule_twilio_sms",
                                         args="[id]"),
                               restrict=restrict_a)
                          )
        return output
    s3.postp = postp

    return s3_rest_controller()

# -----------------------------------------------------------------------------
def workflow():
    """
        RESTful CRUD controller for workflows
            - appears in the administration menu
    """

    if not auth.s3_has_role(ADMIN):
        session.error = UNAUTHORISED
        redirect(URL(f="index"))

    table = s3db.msg_workflow
    table.source_task_id.label = T("Message Source")
    table.source_task_id.comment = DIV(DIV(_class="tooltip",
            _title="%s|%s" % (T("Message Source"),
                              T("This is the name of the username for the Inbound Message Source."))))
    table.workflow_task_id.label = T("Parsing Workflow")
    table.workflow_task_id.comment = DIV(DIV(_class="tooltip",
                _title="%s|%s" % (T("Parsing Workflow"),
                                  T("This is the name of the parsing functionn used as a workflow."))))

    # CRUD Strings
    s3.crud_strings["msg_workflow"] = Storage(
        title_display=T("Setting Details"),
        title_list=T("Parser Settings"),
        title_create=T("Add Parser Settings"),
        title_update=T("Edit Parser Settings"),
        title_search=T("Search Parser Settings"),
        label_list_button=T("View Settings"),
        label_create_button=T("Add Parser Settings"),
        msg_record_created=T("Setting added"),
        msg_record_deleted=T("Parser Setting deleted"),
        msg_list_empty=T("No Settings currently defined"),
        msg_record_modified=T("Message Parser settings updated")
    )

    s3db.configure("msg_workflow", listadd=True, deletable=True)

    def prep(r):
        if r.interactive:
            import inspect
            import sys

            parser = settings.get_msg_parser()
            module_name = "applications.%s.private.templates.%s.parser" % \
                (appname, parser)
            __import__(module_name)
            mymodule = sys.modules[module_name]
            S3Parsing = mymodule.S3Parsing()

            mtable = s3db.msg_inbound_email_settings
            ttable = s3db.msg_twilio_inbound_settings
            source_opts = []
            append = source_opts.append
            records = db(mtable.id > 0).select(mtable.username)
            for record in records:
                append(record.username)

            records = db(ttable.deleted == False).select(ttable.account_name)
            for record in records:
                append(record.account_name)

            # Dynamic lookup of the parsing functions in S3Parsing class.
            parsers = inspect.getmembers(S3Parsing, predicate=inspect.isfunction)
            parse_opts = []
            for parser in parsers:
                parse_opts += [parser[0]]

            r.table.source_task_id.requires = IS_IN_SET(source_opts, zero=None)
            r.table.workflow_task_id.requires = IS_IN_SET(parse_opts, \
                                                          zero=None)
        return True
    s3.prep = prep

    def postp(r, output):

        wtable = s3db.msg_workflow
        stable = db["scheduler_task"]

        s3_action_buttons(r)
        query = stable.enabled == False
        records = db(query).select()
        rows = []
        for record in records:
            if "workflow" and "source" in record.vars:
                r = record.vars.split("\"workflow\":")[1]
                s = r.split("}")[0]
                s = s.split("\"")[1].split("\"")[0]

                u = record.vars.split("\"source\":")[1]
                v = u.split(",")[0]
                v = v.split("\"")[1]

                query = (wtable.workflow_task_id == s) & \
                        (wtable.source_task_id == v)
                record1 = db(query).select(wtable.id)
                if record1:
                    for rec in record1:
                        rows += [rec]

        restrict_e = [str(row.id) for row in rows]

        query = stable.enabled == True
        records = db(query).select()
        rows = []
        for record in records:
            if "workflow" and "source" in record.vars:
                r = record.vars.split("\"workflow\":")[1]
                s = r.split("}")[0]
                s = s.split("\"")[1].split("\"")[0]

                u = record.vars.split("\"source\":")[1]
                v = u.split(",")[0]
                v = v.split("\"")[1]

                query = (wtable.workflow_task_id == s) & \
                        (wtable.source_task_id == v)
                record1 = db(query).select(wtable.id)
                if record1:
                    for rec in record1:
                        rows += [rec]

        restrict_d = [str(row.id) for row in rows]

        rows = []
        records = db(stable.id > 0).select(stable.vars)
        tasks = [record.vars for record in records]
        parser1 = []
        for task in tasks:
            if "workflow" in task:
                r = task.split("\"workflow\":")[1]
                s = r.split("}")[0]
                s = s.split("\"")[1].split("\"")[0]

                parser1 += [s]
        parser2 = []
        for task in tasks:
            if "source" in task:
                u = task.split("\"source\":")[1]
                v = u.split(",")[0]
                v = v.split("\"")[1]
                parser2 += [v]


        workflows = db(wtable.id > 0).select(wtable.id,
                                             wtable.workflow_task_id,
                                             wtable.source_task_id)

        for workflow in workflows :
            if workflow.workflow_task_id and workflow.source_task_id:
                if (workflow.workflow_task_id not in parser1) or \
                   (workflow.source_task_id not in parser2):
                    rows += [workflow]

        restrict_a = [str(row.id) for row in rows]

        s3.actions = \
        s3.actions + [
                       dict(label=str(T("Enable")),
                            _class="action-btn",
                            url=URL(f="enable_parser",
                                    args="[id]"),
                            restrict=restrict_e)
                      ]

        s3.actions.append(dict(label=str(T("Disable")),
                                        _class="action-btn",
                                        url=URL(f="disable_parser",
                                                  args="[id]"),
                                        restrict=restrict_d)
                                   )

        s3.actions.append(dict(label=str(T("Activate")),
                                        _class="action-btn",
                                        url=URL(f="schedule_parser",
                                                  args="[id]"),
                                        restrict=restrict_a)
                                   )

        return output
    s3.postp = postp

    return s3_rest_controller()

# -----------------------------------------------------------------------------
def schedule_parser():
    """
        Schedules different parsing workflows.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Workflow not specified!")
        redirect(URL(f="workflow"))

    wtable = s3db.msg_workflow
    record = db(wtable.id == id).select(wtable.workflow_task_id,
                                        wtable.source_task_id,
                                        limitby=(0, 1)).first()
    workflow = record.workflow_task_id
    source = record.source_task_id

    s3task.schedule_task("msg_parse_workflow",
                         vars={"workflow": workflow, "source": source},
                         period=300, # seconds
                         timeout=300, # seconds
                         repeats=0    # unlimited
                         )

    redirect(URL(f="workflow"))

# -----------------------------------------------------------------------------
def schedule_email():
    """
        Schedules different Email Sources.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Source not specified!")
        redirect(URL(f="inbound_email_settings"))

    mtable = s3db.msg_inbound_email_settings
    record = db(mtable.id == id).select(mtable.username,
                                        limitby=(0, 1)).first()
    username = record.username

    s3task.schedule_task("msg_process_inbound_email",
                         vars={"username": username},
                         period=300, # seconds
                         timeout=300, # seconds
                         repeats=0    # unlimited
                         )

    redirect(URL(f="inbound_email_settings"))

# -----------------------------------------------------------------------------
def schedule_twilio_sms():
    """
        Schedules different Twilio SMS Sources.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Source not specified!")
        redirect(URL(f="twilio_inbound_settings"))

    ttable = s3db.msg_twilio_inbound_settings
    record = db(ttable.id == id).select(ttable.account_name,
                                        limitby=(0, 1)).first()
    account_name = record.account_name

    s3task.schedule_task("msg_twilio_inbound_sms",
                         vars={"account": account_name},
                         period=300, # seconds
                         timeout=300, # seconds
                         repeats=0    # unlimited
                         )

    redirect(URL(f="twilio_inbound_settings"))

# -----------------------------------------------------------------------------
def disable_parser():
    """
        Disables different parsing workflows.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Workflow not specified!")
        redirect(URL(f="workflow"))

    stable = s3db.scheduler_task
    wtable = s3db.msg_workflow

    records = db(stable.id > 0).select()
    workflow = db(wtable.id == id).select(wtable.workflow_task_id,
                                          wtable.source_task_id,
                                          limitby=(0, 1)).first()
    for record in records:
        if "workflow" and "source" in record.vars:
            r = record.vars.split("\"workflow\":")[1]
            s = r.split("}")[0]
            s = s.split("\"")[1].split("\"")[0]

            u = record.vars.split("\"source\":")[1]
            v = u.split(",")[0]
            v = v.split("\"")[1]

            if (s == workflow.workflow_task_id) and (v == workflow.source_task_id) :
                db(stable.id == record.id).update(enabled=False)

    redirect(URL(f="workflow"))

# -----------------------------------------------------------------------------
def disable_email():
    """
        Disables different Email Sources.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Source not specified!")
        redirect(URL(f="inbound_email_settings"))

    stable = s3db.scheduler_task
    mtable = s3db.msg_inbound_email_settings

    records = db(stable.id > 0).select()
    msettings = db(mtable.id == id).select(limitby=(0, 1)).first()
    for record in records:
        if "username" in record.vars:
            r = record.vars.split("\"username\":")[1]
            s = r.split("}")[0]
            s = s.split("\"")[1].split("\"")[0]

            if (s == msettings.username) :
                db(stable.id == record.id).update(enabled=False)

    redirect(URL(f="inbound_email_settings"))

# -----------------------------------------------------------------------------
def disable_twilio_sms():
    """
        Disables different Twilio SMS Sources.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Source not specified!")
        redirect(URL(f="twilio_inbound_settings"))

    stable = s3db.scheduler_task
    ttable = s3db.msg_twilio_inbound_settings

    records = db(stable.id > 0).select()
    tsettings = db(ttable.id == id).select(limitby=(0, 1)).first()
    for record in records:
        if "account" in record.vars:
            r = record.vars.split("\"account\":")[1]
            s = r.split("}")[0]
            s = s.split("\"")[1].split("\"")[0]

            if (s == tsettings.account_name) :
                db(stable.id == record.id).update(enabled=False)

    redirect(URL(f="twilio_inbound_settings"))

# -----------------------------------------------------------------------------
def enable_email():
    """
        Enables different Email Sources.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Source not specified!")
        redirect(URL(f="inbound_email_settings"))

    stable = s3db.scheduler_task
    mtable = s3db.msg_inbound_email_settings

    records = db(stable.id > 0).select()
    msettings = db(mtable.id == id).select(mtable.ALL).first()
    for record in records:
        if "username" in record.vars:
            r = record.vars.split("\"username\":")[1]
            s = r.split("}")[0]
            s = s.split("\"")[1].split("\"")[0]

            if (s == msettings.username) :
                db(stable.id == record.id).update(enabled=True)

    redirect(URL(f="inbound_email_settings"))

# -----------------------------------------------------------------------------
def enable_twilio_sms():
    """
        Enables different Twilio SMS Sources.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Source not specified!")
        redirect(URL(f="twilio_inbound_settings"))

    stable = s3db.scheduler_task
    ttable = s3db.msg_twilio_inbound_settings

    records = db(stable.id > 0).select()
    tsettings = db(ttable.id == id).select(ttable.ALL).first()
    for record in records:
        if "account" in record.vars:
            r = record.vars.split("\"account\":")[1]
            s = r.split("}")[0]
            s = s.split("\"")[1].split("\"")[0]

            if (s == tsettings.account_name) :
                db(stable.id == record.id).update(enabled=True)

    redirect(URL(f="twilio_inbound_settings"))

# -----------------------------------------------------------------------------
def enable_parser():
    """
        Enables different parsing workflows.
    """

    try:
        id = request.args[0]
    except:
        session.error = T("Workflow not specified!")
        redirect(URL(f="workflow"))

    stable = s3db.scheduler_task
    wtable = s3db.msg_workflow

    records = db(stable.id > 0).select()
    workflow = db(wtable.id == id).select(wtable.workflow_task_id,
                                          wtable.source_task_id,
                                          limitby=(0, 1)).first()

    for record in records:
        if "workflow" and "source" in record.vars:
            r = record.vars.split("\"workflow\":")[1]
            s = r.split("}")[0]
            s = s.split("\"")[1].split("\"")[0]

            u = record.vars.split("\"source\":")[1]
            v = u.split(",")[0]
            v = v.split("\"")[1]

            if (s == workflow.workflow_task_id) and \
               (v == workflow.source_task_id):
                db(stable.id == record.id).update(enabled=True)

    redirect(URL(f="workflow"))

# -----------------------------------------------------------------------------
def email_inbox():
    """
        RESTful CRUD controller for the Email Inbox
        - all Inbound Email Messages go here
    """

    if not auth.s3_logged_in():
        session.error = T("Requires Login!")
        redirect(URL(c="default", f="user", args="login"))

    tablename = "msg_email_inbox"
    table = s3db[tablename]

    s3db.configure(tablename, listadd=False)
    return s3_rest_controller()

# -----------------------------------------------------------------------------
def twilio_inbox():
    """
        RESTful CRUD controller for the Twilio SMS Inbox
        - all Inbound SMS Messages from Twilio go here
    """

    if not auth.s3_logged_in():
        session.error = T("Requires Login!")
        redirect(URL(c="default", f="user", args="login"))

    tablename = "msg_twilio_inbox"
    table = s3db[tablename]

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
    title_display=T("Twilio SMS Inbox"),
    title_list=T("Twilio SMS Inbox"),
    title_update=T("Edit SMS Message"),
    title_search=T("Search Twilio SMS Inbox"),
    label_list_button=T("View Twilio SMS"),
    msg_record_deleted=T("Twilio SMS deleted"),
    msg_list_empty=T("Twilio SMS Inbox empty. "),
    msg_record_modified=T("Twilio SMS updated")
        )

    s3db.configure(tablename, listadd=False)

    return s3_rest_controller()

# -----------------------------------------------------------------------------
@auth.s3_requires_membership(1)
def modem_settings():
    """
        RESTful CRUD controller for modem settings
        - appears in the administration menu
        Multiple Modems can be configured to receive Inbound Messages
    """

    try:
        import serial
    except ImportError:
        session.error = T("Python Serial module not available within the running Python - this needs installing to activate the Modem")
        redirect(URL(c="admin", f="index"))

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    table.modem_port.label = T("Port")
    table.modem_baud.label = T("Baud")
    table.enabled.label = T("Enabled")
    table.modem_port.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Port"),
                          T("The serial port at which the modem is connected - /dev/ttyUSB0, etc on linux and com1, com2, etc on Windows"))))
    table.modem_baud.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Baud"),
                          T("Baud rate to use for your modem - The default is safe for most cases"))))
    table.enabled.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Enabled"),
                          T("Unselect to disable the modem"))))

    # CRUD Strings
    ADD_SETTING = T("Add Setting")
    s3.crud_strings[tablename] = Storage(
        title_create=ADD_SETTING,
        title_display=T("Setting Details"),
        title_list=T("Settings"),
        title_update=T("Edit Modem Settings"),
        title_search=T("Search Settings"),
        label_list_button=T("View Settings"),
        label_create_button=ADD_SETTING,
        msg_record_created=T("Setting added"),
        msg_record_modified=T("Modem settings updated"),
        msg_record_deleted=T("Setting deleted"),
        msg_list_empty=T("No Settings currently defined")
    )

    s3db.configure(tablename,
                    #deletable=False,
                    #listadd=False,
                    #update_next = URL(args=[1, "update"])
                    )
    #response.menu_options = admin_menu_options
    return s3_rest_controller()


#------------------------------------------------------------------------------
@auth.s3_requires_membership(1)
def smtp_to_sms_settings():
    """
        RESTful CRUD controller for SMTP to SMS settings
        - appears in the administration menu
        Only 1 of these ever in existence
    """

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    table.address.label = T("Address")
    table.subject.label = T("Subject")
    table.enabled.label = T("Enabled")
    table.address.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Address"),
                          T("Email Address to which to send SMS messages. Assumes sending to phonenumber@address"))))
    table.subject.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Subject"),
                          T("Optional Subject to put into Email - can be used as a Security Password by the service provider"))))
    table.enabled.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Enabled"),
                          T("Unselect to disable this SMTP service"))))

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
        title_update=T("Edit SMTP to SMS Settings"),
        msg_record_modified=T("SMTP to SMS settings updated"),
    )

    s3db.configure(tablename,
                    deletable=False,
                    listadd=False,
                    update_next=URL(args=[1, "update"]))
    #response.menu_options = admin_menu_options
    return s3_rest_controller()


#------------------------------------------------------------------------------
@auth.s3_requires_membership(1)
def api_settings():
    """
        RESTful CRUD controller for Web API settings
        - appears in the administration menu
        Only 1 of these ever in existence
    """

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    table.url.label = T("URL")
    table.to_variable.label = T("To variable")
    table.message_variable.label = T("Message variable")
    table.enabled.label = T("Enabled")
    table.url.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("URL"),
                          T("The URL of your web gateway without the post parameters"))))
    table.parameters.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Parameters"),
                          T("The post variables other than the ones containing the message and the phone number"))))
    table.message_variable.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Message Variable"),
                          T("The post variable on the URL used for sending messages"))))
    table.to_variable.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("To variable"),
                          T("The post variable containing the phone number"))))
    table.enabled.comment = DIV(DIV(_class="tooltip",
        _title="%s|%s" % (T("Enabled"),
                          T("Unselect to disable this API service"))))

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
        title_update=T("Edit Web API Settings"),
        msg_record_modified=T("Web API settings updated"),
    )

    s3db.configure(tablename,
                    deletable=False,
                    listadd=False,
                    update_next=URL(args=[1, "update"]))
    #response.menu_options = admin_menu_options
    return s3_rest_controller()


# -----------------------------------------------------------------------------
@auth.s3_requires_membership(1)
def tropo_settings():
    """
        RESTful CRUD controller for Tropo settings
        - appears in the administration menu
        Only 1 of these ever in existence
    """

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    table.token_messaging.label = T("Tropo Messaging Token")
    table.token_messaging.comment = DIV(DIV(_class="stickytip",
                                            _title="%s|%s" % (T("Tropo Messaging Token"),
                                                              T("The token associated with this application on") + " <a href='https://www.tropo.com/docs/scripting/troposessionapi.htm' target=_blank>Tropo.com</a>")))
    #table.token_voice.label = T("Tropo Voice Token")
    #table.token_voice.comment = DIV(DIV(_class="stickytip",_title=T("Tropo Voice Token") + "|" + T("The token associated with this application on") + " <a href='https://www.tropo.com/docs/scripting/troposessionapi.htm' target=_blank>Tropo.com</a>"))
    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
        title_update=T("Edit Tropo Settings"),
        msg_record_modified=T("Tropo settings updated"),
    )

    s3db.configure(tablename,
                    deletable=False,
                    listadd=False,
                    update_next=URL(args=[1, "update"]))
    #response.menu_options = admin_menu_options
    return s3_rest_controller()


# -----------------------------------------------------------------------------
@auth.s3_requires_membership(1)
def twitter_settings():
    """
        RESTful CRUD controller for Twitter settings
        - appears in the administration menu
        Only 1 of these ever in existence
    """

    try:
        import tweepy
    except:
        session.error = T("tweepy module not available within the running Python - this needs installing for non-Tropo Twitter support!")
        redirect(URL(c="admin", f="index"))

    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    # CRUD Strings
    s3.crud_strings[tablename] = Storage(
        title_update=T("Authenticate system's Twitter account"),
        msg_record_modified=T("System's Twitter account updated"),
    )

    def prep(r):
        if not (settings.twitter.oauth_consumer_key and settings.twitter.oauth_consumer_secret):
            session.error = T("You should edit Twitter settings in models/000_config.py")
            return True
        oauth = tweepy.OAuthHandler(settings.twitter.oauth_consumer_key,
                                    settings.twitter.oauth_consumer_secret)

        #tablename = "%s_%s" % (module, resourcename)
        #table = db[tablename]
        table = r.table

        if r.http == "GET" and r.method in ("create", "update"):
            # We're showing the form
            try:
                session.s3.twitter_oauth_url = oauth.get_authorization_url()
                session.s3.twitter_request_key = oauth.request_token.key
                session.s3.twitter_request_secret = oauth.request_token.secret
            except tweepy.TweepError:
                session.error = T("Problem connecting to twitter.com - please refresh")
                return True
            table.pin.readable = True
            table.pin.label = SPAN(T("PIN number "),
                A(T("from Twitter"), _href=T(session.s3.twitter_oauth_url), _target="_blank"),
                " (%s)" % T("leave empty to detach account"))
            table.pin.value = ""
            table.twitter_account.label = T("Current Twitter account")
            return True
        else:
            # Not showing form, no need for pin
            table.pin.readable = False
            table.pin.label = T("PIN") # won't be seen
            table.pin.value = ""       # but let's be on the safe side
        return True
    s3.prep = prep

    # Post-processor
    def user_postp(r, output):
        output["list_btn"] = ""
        return output
    s3.postp = user_postp

    #response.menu_options = admin_menu_options
    s3db.configure(tablename, listadd=False, deletable=False)
    return s3_rest_controller()

# =============================================================================
# The following functions hook into the pr functions:
#
def group():
    """ RESTful CRUD controller """

    if auth.is_logged_in() or auth.basic():
        pass
    else:
        redirect(URL(c="default", f="user", args="login",
        vars={"_next":URL(c="msg", f="group")}))

    module = "pr"
    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    # Hide unnecessary fields
    table.description.readable = table.description.writable = False

    # Do not show system groups
    s3.filter = (table.system == False)

    return s3_rest_controller(module, resourcename, rheader=s3db.pr_rheader)


# -----------------------------------------------------------------------------
def group_membership():
    """ RESTful CRUD controller """

    if auth.is_logged_in() or auth.basic():
        pass
    else:
        redirect(URL(c="default", f="user", args="login",
        vars={"_next":URL(c="msg", f="group_membership")}))

    table = s3db.pr_group_membership

    # Hide unnecessary fields
    table.description.readable = table.description.writable = False
    table.comments.readable = table.comments.writable = False
    table.group_head.readable = table.group_head.writable = False

    return s3_rest_controller("pr", resourcename)

# -----------------------------------------------------------------------------
def contact():
    """ Allows the user to add, update and delete their contacts """

    table = s3db.pr.contact
    ptable = s3db.pr_person

    if auth.is_logged_in() or auth.basic():
        s3.filter = (table.pe_id == auth.user.pe_id)
    else:
        redirect(URL(c="default", f="user", args="login",
            vars={"_next":URL(c="msg", f="contact")}))

    # These fields will be populated automatically
    table.name.writable = table.name.readable = False
    table.pe_id.writable = table.pe_id.readable = False
    table.person_name.writable = table.person_name.readable = False
    table.id.writable = False
    #table.id.readable = False

    def msg_contact_onvalidation(form):
        """ This onvalidation method adds the person id to the record """
        if auth.user:
            form.vars.pe_id = auth.user.pe_id

    s3db.configure(table._tablename,
                    onvalidation=msg_contact_onvalidation)

    def msg_contact_restrict_access(r):
        """ The following restricts update and delete access to contacts not owned by the user """
        if r.id :
            pe_id = r.record.pe_id
            if auth.user and auth.user.pe_id == pe_id:
                return True
            else:
                session.error = T("Access denied")
                return dict(bypass=True, output=redirect(URL(r=request)))
        else:
            return True
    s3.prep = msg_contact_restrict_access

    response.menu_options = []
    return s3_rest_controller("pr", resourcename)

# -----------------------------------------------------------------------------
def search():
    """
        Do a search of groups which match a type
        - used for auto-completion
    """

    if not (auth.is_logged_in() or auth.basic()):
        # Not allowed
        return

    # JQuery UI Autocomplete uses 'term' instead of 'value'
    # (old JQuery Autocomplete uses 'q' instead of 'value')
    value = request.vars.term or request.vars.q
    type = request.get_vars.get("type", None)
    if value:
        # Call the search function
        if type:
            items = person_search(value, type)
        else:
            items = person_search(value)
        # Encode in JSON
        item = json.dumps(items)
        response.headers["Content-Type"] = "application/json"
        return item
    return

# -----------------------------------------------------------------------------
def recipient_represent(id, default_label=""):
    """ Simplified output as-compared to pr_pentity_represent """

    output = ""
    table = s3db.pr_pentity
    pe = db(table.pe_id == id).select(table.instance_type,
                                      limitby=(0, 1)).first()
    if not pe:
        return output
    instance_type = pe.instance_type
    table = db.get(instance_type, None)
    if not table:
        return output
    if instance_type == "pr_person":
        person = db(table.pe_id == id).select(table.first_name,
                                              table.middle_name,
                                              table.last_name,
                                              limitby=(0, 1)).first()
        if person:
            output = s3_fullname(person)
    elif instance_type == "pr_group":
        group = db(table.pe_id == id).select(table.name,
                                             limitby=(0, 1)).first()
        if group:
            output = group.name
    return output

# -----------------------------------------------------------------------------
def person_search(value, type=None):
    """ Search for People & Groups which match a search term """

    # Shortcuts
    groups = s3db.pr_group
    persons = s3db.pr_person

    items = []

    # We want to do case-insensitive searches
    # (default anyway on MySQL/SQLite, but not PostgreSQL)
    value = value.lower()

    if type:
        represent = recipient_represent
    else:
        represent = s3db.pr_pentity_represent

    if type == "pr_group" or not type:
        # Check Groups
        query = (groups["name"].lower().like("%" + value + "%")) & (groups.deleted == False)
        rows = db(query).select(groups.pe_id)
        for row in rows:
            items.append({"id":row.pe_id, "name":represent(row.pe_id, default_label="")})

    if type == "pr_person" or not type:
        # Check Persons
        deleted = (persons.deleted == False)

        # First name
        query = (persons["first_name"].lower().like("%" + value + "%")) & deleted
        rows = db(query).select(persons.pe_id, cache=s3db.cache)
        for row in rows:
            items.append({"id":row.pe_id, "name":represent(row.pe_id, default_label="")})

        # Middle name
        query = (persons["middle_name"].lower().like("%" + value + "%")) & deleted
        rows = db(query).select(persons.pe_id, cache=s3db.cache)
        for row in rows:
            items.append({"id":row.pe_id, "name":represent(row.pe_id, default_label="")})

        # Last name
        query = (persons["last_name"].lower().like("%" + value + "%")) & deleted
        rows = db(query).select(persons.pe_id, cache=s3db.cache)
        for row in rows:
            items.append({"id":row.pe_id, "name":represent(row.pe_id, default_label="")})

    return items

# -----------------------------------------------------------------------------
def subscription():

    return s3_rest_controller()

def test():
    return "response.session_id: %s" % response.session_id

# -----------------------------------------------------------------------------
def search_subscription_notifications():
    import cPickle
    import cgi
    import urlparse
    import urllib
    from s3.s3resource import S3Resource, S3ResourceField, S3ResourceFilter, S3FieldSelector
    import urllib2
    import uuid
    from gluon.tools import fetch
    import Cookie
    import json
    from s3.s3utils import s3_auth_user_represent

    resource = S3Resource("pr", "saved_search")
    frequency_field = S3ResourceField(resource, "saved_search.notification_frequency")

    if request.args:
        if request.args[0] in dict(frequency_field.requires.options()):
            frequency = request.args[0]
            table = s3db.pr_saved_search

            saved_searches = db((table.notification_frequency == frequency) & (table.deleted != True)).select()
            if saved_searches:

                notifiers = {
                    "default": search_subscription_notifier_default,
                    "EMAIL": search_subscription_notifier_email,
                    #"TWITTER": search_subscription_formatter_twitter,
                }

                # Use the current session to make a new request
                cookie = Cookie.SimpleCookie()
                cookie[current.response.session_id_name] = current.response.session_id

                for search in saved_searches:
                    # fetch the latest records from the search

                    url = "%s%s" % (settings.get_base_public_url(), search.url)

                    auth_token = uuid.uuid4()
                    search.update_record(auth_token=auth_token)
                    db.commit()

                    parsed_url = urlparse.urlparse(url)
                    query_parameters = urlparse.parse_qs(parsed_url.query)

                    # query_string = "%s&%s" % (
                    #     parsed_url.query,
                    #     urllib.urlencode(
                    #     )
                    # )
                    # url_list = list(parsed_url)
                    # url_list[4] = query_string

                    # impersonate user
                    #user_id = current.auth.s3_get_user_id(search.pe_id)

                    #if user_id:
                    #    current.auth.s3_impersonate(user_id)
                    #else:
                    #    current.auth.s3_impersonate(None)

                    #print "Impersonating %s" % s3_auth_user_represent(current.auth.user_id)


                    # unlock the session or else the fetch will hang
                    session._unlock(response)

                    if search.notification_batch:
                        # put the URL back together
                        #new_url = urlparse.urlunparse(url_list)
                        new_url = URL(
                            scheme=True,
                            c=search.controller,
                            f=search.function,
                            args=[
                                "search",
                            ],
                            vars={
                                "search_subscription": auth_token,
                                "format": "email",
                                "%s.modified_on__ge" % (search.resource_name): search.last_checked,
                            }
                        )
                        new_url = "%s&%s" % (
                            new_url,
                            search.filters
                        )
                        print new_url

                        message = fetch(new_url, cookie=cookie)

                        print message
                        continue

                        # Send the email
                        msg.send_by_pe_id(
                            search.pe_id,
                            subject="%s Search Notification %s" % (
                                settings.get_system_name_short(),
                                search.name,
                            ),
                            message=message,
                            sender_pe_id=None,
                            pr_message_method="EMAIL",
                            sender="noreply@sahana.com",
                            fromaddress="sahana@sahana.com"
                        )
                    else:
                        json_url = URL(
                            scheme=True,
                            c=search.controller,
                            f=search.function,
                            args=[
                                "search",
                            ],
                            vars={
                                "search_subscription": auth_token,
                                "format": "json",
                                "%s.modified_on__ge" % (search.resource_name): search.last_checked,
                            }
                        )
                        json_url = "%s&%s" % (
                            json_url,
                            search.filters
                        )
                        print json_url

                        # fetch the record list as json
                        json_string = fetch(json_url, cookie=cookie)

                        # log out after making the request
                        records = json.loads(json_string)

                        for record in records:
                            record_url = URL(
                                scheme=True,
                                c=search.controller,
                                f=search.function,
                                args=[
                                    "search",
                                ],
                                vars={
                                    "search_subscription": auth_token,
                                    "format": "email",
                                    "%s.id__eq" % search.resource_name: record["id"], 
                                }
                            )
                            print record_url

                            message = fetch(record_url, cookie=cookie)

                            print message
                            continue

                            # Send the email
                            msg.send_by_pe_id(
                                search.pe_id,
                                subject="%s Search Notification %s" % (
                                    settings.get_system_name_short(),
                                    search.name,
                                ),
                                message=message,
                                sender_pe_id=None,
                                pr_message_method="EMAIL",
                                sender="noreply@sahana.com",
                                fromaddress="sahana@sahana.com"
                            )

                    # Create the resource
                    #search_resource = S3Resource(search.prefix, search.resource_name)
                    #filters = S3ResourceFilter.parse_url_query(search_resource, filters)[resource_name]

                    # Add the saved filters
                    #for filter in filters:
                    #    search_resource.add_filter(filter)

                    # Only records modified after the last_checked datetime
                    #search_resource.add_filter(S3FieldSelector("modified_on") >= search.last_checked)

                    # if records:
                    #     if search.notification_method in notifiers:
                    #         method = search.notification_method
                    #     else:
                    #         method = "default"

                    #     notifiers[method](search, search_resource, records)
                return
                # Update the saved searches to indicate they've just been checked
                db(
                    (table.notification_frequency == frequency) & \
                    (table.deleted != True)
                ).update(
                    last_checked=datetime.datetime.utcnow()
                )
                return ""

    raise HTTP(404) # not found

# -----------------------------------------------------------------------------
def search_subscription_notifier_default(search, resource, records, **kwargs):
    """
        Gets records from a resource and returns an HTML list.
        This is only used when there isn't a dedicated formatter
        for a particular method. Quick and dirty.

        @param search: the saved search object
        @param resource: the resource, with filters, to get records from
    """
    import cgi

    output = ""

    # Fetched the records from the resource
    for row in resource.sqltable(as_rows=True):
        url = URL(c=resource.prefix, f=resource.name, args=row.id)
        #string = current.manager.represent(field, record=row)
        output += "<li><a href=\"%s\">%s</a></li>" % (url, cgi.escape(str(row)))

    return output

# -----------------------------------------------------------------------------
def search_subscription_notifier_email(search, resource, records, **kwargs):
    """
        Sends an email for a search subscription. Email contains an HTML table
        with one or more records.

        @param search: the saved search object
        @param resource: the resource, with filters, to get records from
    """

    fields = [f for f in resource.readable_fields() if f.name != "id"] # We don't want to show the "id" field at all
    head_row = TR([TH(f.label) for f in fields if f.name != "id"])
    new_rows = []
    mod_rows = []

    json_resource_name = "$_%s_%s" % (
        resource.prefix,
        resource.name
    )

    for row in records[json_resource_name]:
        first_cell = False # disabled
        row_cells = []

        for f in fields:
            if f.name in row:
                field = row[f.name]
            elif "@%s" % f.name in row:
                field = row["@%s" % f.name]
            elif "$k_%s" % f.name in row:
                field = row["$k_%s" % f.name]
            else:
                field = None

            if field:
                #rep_value = current.manager.represent(f, record=row)
                #rep_value = row.get(f.name, "")
                #rep_value = f.represent(row[f.name])
                if isinstance(field, dict):
                    rep_value = field["$"]
                else:
                    rep_value = field

                # Hyperlink the text in the first
                # cell to the record page
                if first_cell:
                    url = URL(
                        scheme=True,
                        c=search.controller,
                        f=search.function,
                        args=row["id"],
                    )
                    rep_value = A(
                        rep_value,
                        _href=url,
                    )
                    first_cell = False
            else:
                rep_value = ""

            row_cells.append(TD(rep_value))

        if row_cells:
            tr = TR(*row_cells)

            # Records are either "new" or "modified"
            if "created_on" in row:
                if row.created_on >= search.last_checked:
                    new_rows.append(tr)
            else:
                mod_rows.append(tr)

    def send(new_rows=[], mod_rows=[]):
        """
            Puts the rows into tables, renders them
            using a template, and then
            sends the notification (email)
        """
        if not new_rows and not mod_rows:
            return

        # Generate a table for the new records
        if new_rows:
            new_table = TABLE(
                THEAD(head_row),
                TBODY(*new_rows),
            )
        else:
            new_table = None

        # Generate a table for updated records
        if mod_rows:
            mod_table = TABLE(
                THEAD(head_row),
                TBODY(*mod_rows),
            )
        else:
            mod_table = None

        # Render the records via a template
        message = response.render(
            "msg/notification_email.html",
            {
                "search": search,
                "new_table": new_table,
                "mod_table": mod_table,
                "system_name": settings.get_system_name(),
                "resource_name": resource.name,
            }
        )

        #print "Message: %s" % message
        #return

        # Send the email
        msg.send_by_pe_id(
            search.pe_id,
            subject="%s Search Notification %s" % (
                settings.get_system_name_short(),
                search.name,
            ),
            message=message,
            sender_pe_id=None,
            pr_message_method="EMAIL",
            sender="noreply@sahana.com",
            fromaddress="sahana@sahana.com"
        )

    if search.notification_batch:
        # Batch notifications send all rows at once
        send(
            new_rows,
            mod_rows,
        )
    else:
        # Non-batch notifications send each row in its own message
        for row in new_rows:
            send(new_rows=[row])

        for row in mod_rows:
            send(mod_rows=[row])

# =============================================================================
# Enabled only for testing:
#
@auth.s3_requires_membership(1)
def tag():
    """ RESTful CRUD controller """


    tablename = "%s_%s" % (module, resourcename)
    table = s3db[tablename]

    # Load all models
    s3db.load_all_models()
    table.resource.requires = IS_IN_SET(db.tables)

    s3db.configure(tablename, listadd=False)
    return s3_rest_controller()

# END ================================================================================
