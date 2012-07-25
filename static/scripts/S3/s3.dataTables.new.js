function toggle_cell_truncation(cell, event) {
	/*
	* Truncates the string contents of a cell
	* Adds a clickable ellipsis or full-stop to toggle the truncation
	*/
	var cell = $(cell);
	var text = cell.text();
	var max_string_length = 60;

	if (cell.hasClass("truncated")) {
		// replaces the currently truncated string with the original data
		// the period can be clicked to truncate again
		var instance_id = cell.closest("table").data("instance");
		var full_text = S3.dataTablesInstances[instance_id].instance.fnGetData(cell.get(0));
		cell.html(full_text).append('<a class="ellipsis" title="' + _("Truncate text") + '">.</a>');
		cell.removeClass("truncated");
	}
	else if (text.length > max_string_length) {
		// truncates the cell text and adds an ellipsis
		var truncated_text = text.substring(0, max_string_length);
		cell.html(truncated_text).append('<a class="ellipsis" title="' + _("Show full text") + '">&#8230;</a>');
		cell.addClass("truncated");
	}
}

S3.pluginDefaults = {
	"dataTables": {
		"iDisplayLength": 25,
		"bProcessing": true,
		"bServerSide": false,
		"bFilter": true,
		"aaSorting": [[1, 'asc']],
		"sDom": 'fril<"dataTable_table"t>pi',
		"sPaginationType": 'full_numbers',
        "aLengthMenu": [[ 25, 50, -1], [ 25, 50, S3.i18n.all]],
		"fnRowCallback": function(nRow, aData, iDisplayIndex) {
			var instance_id = this.data("instance");
			var instance = S3.dataTablesInstances[instance_id];
			var $row = $(nRow);

			if (instance.bulk_actions) {
				var row_id = parseInt(aData[0]);
				chbx = $('<input/>').attr({"value": row_id,
				                           "name": "action_selected",
				                           "type": "checkbox"});
				$row.children().first().html(chbx);
			}

			if (instance.row_actions) {
				var row_id = parseInt(aData[0]);

				$row.children().last().html("");

				for (var i=0; i < instance.row_actions.length; i++) {
					var action = instance.row_actions[i];

					if (action.restrict.indexOf(row_id) != -1) {
						btn = $('<a/>').attr({"href": action.url.replace("%5Bid%5D", row_id)})
									   .text(action.label)
									   .addClass(".btn")
									   .addClass(action.css);
						$row.children().last().append(btn);
					}
				}
			}

			// if the cell only contains a string,
			// truncate it if it's too long.
			for (var i=0; i < nRow.children.length; i++) {
				if (nRow.children[i].children.length == 0) {
					toggle_cell_truncation(nRow.children[i]);
				}
			}

			// temp
			//$row.children(":eq(1)").wrapInner('<a href="' + row_id + '"/>');
		}
	}
};

$(document).ready(function() {
	// initialise all datatables
	$("table.dataTable").each(function(index) {
		var table = $(this);
		var options = $.extend(
			{},
			S3.pluginDefaults.dataTables,
			S3.dataTablesInstances[index].options
		);
		S3.dataTablesInstances[index]["instance"] = table.data("instance", index).dataTable(options);
	});

	// Update the bulk-action form "action" attribute on page load
	$("form.dataTable-actions select[name='action']").each(function(index) {
		$(this).closest('form').attr('action', this.value);
	}).on('change', function() {
		$(this).closest('form').attr('action', this.value);
	});

    // Clicking on the ellipsis or full-stop in a cell toggles the truncation
    $("table.dataTable").on("click", "a.ellipsis", function(event) {
		var cell = $(this).closest("td").get(0);
		toggle_cell_truncation(cell);
    });
});
