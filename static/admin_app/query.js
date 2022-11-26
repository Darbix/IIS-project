var selected;

document.addEventListener("DOMContentLoaded", function() {
	InitDropdown();
});

function InitDropdown() {
	selected = document.getElementById("table_dropdown").value;
	var selection = document.getElementById("table_dropdown").value;

	document.getElementById("sort_by_" + selection).hidden = false;
	document.getElementById("sort_by_selection_" + selection).disabled = false;
}

function UpdateDropdown(selection) {
	document.getElementById("sort_by_" + selected).hidden = true;
	document.getElementById("sort_by_selection_" + selected).disabled = true;

	document.getElementById("sort_by_" + selection).hidden = false;
	document.getElementById("sort_by_selection_" + selection).disabled = false;

	selected = selection;
}

function UpdateModalAdd(id) {
	var values_length = document.getElementsByName("table_header").length;
	var btn = document.getElementById("modal_button_submit");
	btn.innerHTML = "Add";
	btn.name = "add";

	document.getElementById("modalUpdateLabel").innerHTML = "Add new item (raw)";
	for (var i = 0; i < values_length; i++) {
		document.getElementById("modal_row_id_" + i).value = "";
	}
}

function UpdateModal(id) {
	var values = document.getElementsByName("row_id_" + id);
	var btn = document.getElementById("modal_button_submit");
	btn.innerHTML = "Update";
	btn.name = "update";

	document.getElementById("modalUpdateLabel").innerHTML = "Edit item data (raw)";
	for (var i = 0; i < values.length; i++) {
		document.getElementById("modal_row_id_" + i).value = values[i].outerText;
	}
}
