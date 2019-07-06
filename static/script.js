
//String.prototype.format = function() {
//	a = this;
//	for (k in arguments) {
//		a = a.replace("{" + k + "}", arguments[k])
//	}
//	return a
//}

String.prototype.format = String.prototype.f = function() {
	var s = this,
		i = arguments.length;

	while (i--) {
		s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
	}
	return s;
};


var mealOptionsSelected = 1;
var mealOptions = [];


$(document).ready(function () {
//	console.log($("#meal-options option:selected").text());
	
	$("#option2-setup").hide();
	$("#option3-setup").hide();
	$("#option2-title").hide();
	$("#option3-title").hide();
//	$("#option2-setup").show();
//	$("#option3-setup").show();
	
	$("#option1-item1").show();
	$("#option1-item2").hide();
	$("#option1-item3").hide();
	$("#option1-item4").hide();
	$("#option1-item5").hide();
	
	$("#option2-item1").show();
	$("#option2-item2").hide();
	$("#option2-item3").hide();
	$("#option2-item4").hide();
	$("#option2-item5").hide();
	
	$("#option3-item1").show();
	$("#option3-item2").hide();
	$("#option3-item3").hide();
	$("#option3-item4").hide();
	$("#option3-item5").hide();
	
//	var row = $("<tr></tr>");
//	var col1 = $("<td></td>");
//	var col2 = $("<td></td>");
//	var col3 = $("<td></td>");
	
	$("#meal-options").change(function () {
		mealOptionsSelected = $(this).children("option:selected").val();
		
		if (mealOptionsSelected == 1) {
			$("#option2-setup").hide();
			$("#option2-title").hide();
			
			$("#option3-setup").hide();
			$("#option3-title").hide();
		} else if (mealOptionsSelected == 2) {
			$("#option2-setup").show();
			$("#option2-title").show();
			
			$("#option3-setup").hide();
			$("#option3-title").hide();
		} else if (mealOptionsSelected == 3) {
			$("#option2-setup").show();
			$("#option2-title").show();
			
			$("#option3-setup").show();
			$("#option3-title").show();
		}
	});
	
	$("#option1-items").change(function () {
		var totalItems = $(this).children("option:selected").val();
		
		if (totalItems == 1) {
			$("#option1-item1").show();
			$("#option1-item2").hide();
			$("#option1-item3").hide();
			$("#option1-item4").hide();
			$("#option1-item5").hide();
		} else if (totalItems == 2) {
			$("#option1-item1").show();
			$("#option1-item2").show();
			$("#option1-item3").hide();
			$("#option1-item4").hide();
			$("#option1-item5").hide();
		} else if (totalItems == 3) {
			$("#option1-item1").show();
			$("#option1-item2").show();
			$("#option1-item3").show();
			$("#option1-item4").hide();
			$("#option1-item5").hide();
		} else if (totalItems == 4) {
			$("#option1-item1").show();
			$("#option1-item2").show();
			$("#option1-item3").show();
			$("#option1-item4").show();
			$("#option1-item5").hide();
		} else if (totalItems == 5) {
			$("#option1-item1").show();
			$("#option1-item2").show();
			$("#option1-item3").show();
			$("#option1-item4").show();
			$("#option1-item5").show();
		}
	});
	
	$("#option2-items").change(function () {
		var totalItems = $(this).children("option:selected").val();
		
		if (totalItems == 1) {
			$("#option2-item1").show();
			$("#option2-item2").hide();
			$("#option2-item3").hide();
			$("#option2-item4").hide();
			$("#option2-item5").hide();
		} else if (totalItems == 2) {
			$("#option2-item1").show();
			$("#option2-item2").show();
			$("#option2-item3").hide();
			$("#option2-item4").hide();
			$("#option2-item5").hide();
		} else if (totalItems == 3) {
			$("#option2-item1").show();
			$("#option2-item2").show();
			$("#option2-item3").show();
			$("#option2-item4").hide();
			$("#option2-item5").hide();
		} else if (totalItems == 4) {
			$("#option2-item1").show();
			$("#option2-item2").show();
			$("#option2-item3").show();
			$("#option2-item4").show();
			$("#option2-item5").hide();
		} else if (totalItems == 5) {
			$("#option2-item1").show();
			$("#option2-item2").show();
			$("#option2-item3").show();
			$("#option2-item4").show();
			$("#option2-item5").show();
		}
	});
		
		
	$("#option3-items").change(function () {
		var totalItems = $(this).children("option:selected").val();
		
		if (totalItems == 1) {
			$("#option3-item1").show();
			$("#option3-item2").hide();
			$("#option3-item3").hide();
			$("#option3-item4").hide();
			$("#option3-item5").hide();
		} else if (totalItems == 2) {
			$("#option3-item1").show();
			$("#option3-item2").show();
			$("#option3-item3").hide();
			$("#option3-item4").hide();
			$("#option3-item5").hide();
		} else if (totalItems == 3) {
			$("#option3-item1").show();
			$("#option3-item2").show();
			$("#option3-item3").show();
			$("#option3-item4").hide();
			$("#option3-item5").hide();
		} else if (totalItems == 4) {
			$("#option3-item1").show();
			$("#option3-item2").show();
			$("#option3-item3").show();
			$("#option3-item4").show();
			$("#option3-item5").hide();
		} else if (totalItems == 5) {
			$("#option3-item1").show();
			$("#option3-item2").show();
			$("#option3-item3").show();
			$("#option3-item4").show();
			$("#option3-item5").show();
		}
	});
	
//	console.log($("#meal-form"));
	$("#sendData").click(function () {
//		$("#option1-item1").children("td").children("select").children("option:selected").val()
		$("#meal-form").append($("#option1-item1").children("td").children("select").children("option:selected").val());
		console.log($("#meal-form"));
	});
	
	
	
//	console.log("option{0}-item{1}".f(1,12));
//	$("#option1-item1").children("td").children("select").children("option:selected").val();
//	$("#option1-item1").children("td:nth-child(2)").children("input").val();
	
//	var selectItemQuantities = $("<select></select>").attr("id", "option2-items");
	
	
//	$("#meal-form").append(table);
//	$("#meal-form").append(selectItemQuantities);
//	$("#option2-items").append($("<option>", {value: 1, text: 1}));
})