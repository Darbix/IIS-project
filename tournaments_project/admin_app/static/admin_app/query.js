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
