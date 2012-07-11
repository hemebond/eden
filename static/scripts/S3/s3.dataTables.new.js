S3.pluginDefaults = {
	"dataTables": {
		"iDisplayLength": 25,
		"bFilter": true,
		"aaSorting": [[1, 'asc']],
		//"sortFixed": null,
		"sDom": 'fril<"dataTable_table"t>pi',
		"sPaginationType": 'full_numbers'//,
		//"selectionMode": 'Inclusive',
		//"bSort": true,
		//"bDeferRender": true,
		//"aLengthMenu": [[ 25, 50, -1], [ 25, 50, S3.i18n.all]]
	}
};

$(document).ready(function() {
	$(".dataTable").each(function(index) {
		var table = $(this);
		var options = $.extend(
			{},
			S3.pluginDefaults.dataTables,
			S3.dataTablesInstances[index].options
		);
		table.dataTable(options).data("instance", index);
	});
});
