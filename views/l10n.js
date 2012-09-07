{{# These are messages which are translatable & can then be available to Static JavaScript}}
S3.i18n=Object()
S3.i18n.language='{{=s3.language}}'
S3.i18n.ajax_wht='{{=T("We have tried")}}'
S3.i18n.ajax_gvn='{{=T("times and it is still not working. We give in. Sorry.")}}'
S3.i18n.ajax_500='{{=T("Sorry - the server has a problem, please try again later.")}}'
S3.i18n.ajax_dwn='{{=T("There was a problem, sorry, please try again later.")}}'
S3.i18n.ajax_get='{{=T("getting")}}'
S3.i18n.ajax_fmd='{{=T("form data")}}'
S3.i18n.ajax_rtr='{{=T("retry")}}'
S3.i18n.unsaved_changes="{{=T("You have unsaved changes. Click Cancel now, then 'Save' to save them. Click OK now to discard them.")}}"
S3.i18n.datetime_format='{{=T("%Y-%m-%d %H:%M:%S")}}'
S3.i18n.hour='{{=T("Hour")}}'
S3.i18n.minute='{{=T("Minute")}}'
S3.i18n.delete_confirmation='{{=T("Are you sure you want to delete this record?")}}'
S3.i18n.close_map='{{=T("Close map")}}'
S3.i18n.no_match='{{=T("No match")}}'
S3.i18n.in_inv='{{=T("in Stock")}}'
S3.i18n.no_packs='{{=T("No Packs for Item")}}'
S3.i18n.input_number='{{=T("Please enter a number only")}}'
S3.i18n.ac_widget_more_results='{{=T("Greater than 10 matches. Please refine search further")}}'

S3.i18n["Show full text"] = "{{=T("Show full text")}}";
S3.i18n["Truncate text"] = "{{=T("Truncate text")}}";
S3.i18n["View saved search."] = "{{=T("View saved search.")}}";

function _(string) {
	var translated_string = S3.i18n[string];
	if (translated_string == null) {
		return string;
	}
	return translated_string;
}
