// Functions used by S3InlineComponentWidget

var S3InlineComponentWidgetFileCounter = 0;

//TODO more data validation
//TODO before adding a new row, check rows which were added previous - not just the JSON
//TODo produce the DummydisplayValues and DummyJSONValues using a loop - probably don't need a reg-ex anymore!

function S3InlineComponentWidgetAddClick(args) {
	// the input element that will store the formset values
	var currentValuesElement = $("#"+ args.widgetId + "_json");
	var currentValues = currentValuesElement.val();

	var inputBlank = true;

	var fileInputID = "";
	var newFileInputID = "";

	//IE Hack - the navigate away confirm was appearing when this event occured
	//This is a hack, becuase if the use tries to navigate away without making any more changes, they will not be warned
	//ClearNavigateAwayConfirm ();

	var newValue = "";
	var newRow = args.template

	for (var i = 0; i < args.fields.length; i++) {
		fieldname = args.fields[i];

		//Get the value of the new data
		var inputId = args.widgetId + "_" + fieldname;
		var fieldElement = $("#" + inputId);
		var displayValue = "";

		// Need to check siblings because the autocomplete doesn't share
		// the id or name attributes of the original input element
		//var autoCompleteElement = fieldElement.siblings(".ui-autocomplete-input");
		var autoCompleteElement = $("#dummy_" + inputId);

		if (fieldElement.is("select") ) {
			inputValue = fieldElement.val();
			displayValue = $("option:selected", fieldElement).text();
			fieldElement.val("");
		}
		else if (autoCompleteElement.length) {
			//This is an autocomplete
			displayValue = autoCompleteElement.val();
			inputValue = fieldElement.val();

			//MH DRRPP hack - don't allow empty JSON from Autocomplete
			if (fieldname.slice(-3) == "_id" && inputValue == "") {
				displayValue = "";
				break;
			}
			autoCompleteElement.val("");
			fieldElement.val("");
		}
		else if (fieldElement.attr("type") == "file") {
			displayValue = fieldElement.val();
			displayValue = displayValue.replace("fakepath", "...");

			if (displayValue != "") { //There is a file
				fileInputId = inputId;
				newFileInputId = fieldname + S3InlineComponentWidgetFileCounter++;
				inputValue = newFileInputId;
			}
		}
		else {
			displayValue = fieldElement.val();
			fieldElement.val("");

			if (fieldElement.attr("class") == "currency") {
				displayValue = displayValue.replace(/[$,]/g,"");
			}
			if (fieldElement.attr("class") == "double") {
				displayValue = displayValue.replace(/[$,]/g,"");
				if (displayValue) {
					displayValue = parseFloat(displayValue).toFixed(2); // 2dp
				}
			}
			displayValue = displayValue.replace(/'/g,"\'");
			inputValue = displayValue;
		}

		if (displayValue != "") {
			inputBlank = false;
		}

		// escape double quotes
		inputValue = inputValue.replace(/\"/g, "\\\"");

		// replace the placeholders in the template row
		regexDisplay = new RegExp("DISPLAY" + i, "g");
		regexValue = new RegExp("VALUE" + i, "g");

		newRow = newRow.replace(regexDisplay, displayValue);
		newRow = newRow.replace(regexValue, inputValue);

		// add the new field value to the list
		newValue += "\"" + fieldname + "\":\"" + inputValue + "\",";
	}

	newValue = "{" + newValue.slice(0, -1) + "}";

	// Make sure the value is new
	testNewValue = newValue.replace(/([\(\)\[\]])/g, "\\$1");
	if (!inputBlank && !currentValues.match(testNewValue)) {
		if (currentValues != "") {
			currentValues = currentValues + ",";
		}

		//currentValues = currentValues + newcurrentValues;
		currentValues += newValue;

		//Update the Dummy Widget
		currentValuesElement.val(currentValues);

		//Insert the new Row into the table
		$(newRow).insertBefore("#" + args.widgetId + "_input_row");

		if (fileInputId != "") {
			//There is a file input in the Row
			//Change the ID of the old file input
			$("#" + fileInputId).attr("id", newFileInputId);
			$("#" + newFileInputId).attr("name", newFileInputId);

			//Hide the old file input
			$("#" + newFileInputId).hide();

			//add a new file input
			$('<input class="upload" id="' + fileInputId + '" type="file">').insertAfter("#" + newFileInputId)
		}
	}
}

function S3InlineComponentWidgetDelClick(widgetDelete, args) {
	var deleteWidget = $(widgetDelete);
	var rowId = deleteWidget.attr("row_id");
	//var DummyWidgetValue = $("#"+ args.DummyName).val();

	var currentValuesElement = $("#"+ args.widgetId + "_json");
	var currentValues = currentValuesElement.val();

	//IE Hack - the navigate away confirm was appearing when this event occured
	//This is a hack, becuase if the use tries to navigate away without making any more changes, they will not be warned
	//ClearNavigateAwayConfirm ();

	// remove the row from the display
	deleteWidget.closest("tr").remove();

	// test to see if this is an existing entry in the table != 0
	if (rowId != "New") {
		if (currentValues != "") {
			currentValues = currentValues + ",";
		}
		// mark this record for deletion
		currentValues = currentValues + "{\"id\":\"" + rowId + "\", \"deleted\":True},";
	}
	else {
		// the record hasn't been saved
		// delete the marker for this record
		var recordString = "";
		for (i = 0; i < args.fields.length; i++) {
			fieldname = args.fields[i];

			recordString += "\""
			            + fieldname
			            + "\":\""
			            + deleteWidget.attr(fieldname)
			            + "\","
		}
		recordString = "{" + recordString.slice(0,-1) + "}";

		currentValues = currentValues.replace(recordString, "");

		// delete the associated file input element
		$("#" + deleteWidget.attr(args.fields[0]) + ".upload").remove();
	}

	currentValues = currentValues.replace(",,", ",");
	if (currentValues.slice(-1) == ",") {
		currentValues = currentValues.slice(0,-1)
	}

	currentValuesElement.val(currentValues);
}
