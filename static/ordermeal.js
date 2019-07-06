function image() {
	var todayDate = new Date().toISOString().slice(0,10);
	date = todayDate.split('-').join('')
	url = 'https://s3-us-west-2.amazonaws.com/ordermealapp/' + date
	console.log(date);
	document.getElementById("img").innerHTML = "<img height='150' src=" + url + "></img>"
}


function inventory(orders) {
	num_orders = orders.length;
	var totalcost = 0;
	var totalOptionOne = 0;
	var totalOptionTwo = 0;
	for (i = 0; i < num_orders; i++) { 
			totalOptionOne += parseInt(orders[i].mealOption1["N"]);
 			totalOptionTwo += parseInt(orders[i].mealOption2["N"]);
 			totalcost += parseInt(orders[i].totalAmount["N"]);
	}
	document.getElementById("daal_1").innerHTML = totalOptionOne;
	document.getElementById("daal_2").innerHTML = totalOptionTwo;
	document.getElementById("daal_total").innerHTML = (totalOptionOne + totalOptionTwo);
	document.getElementById("bhaji_1").innerHTML = totalOptionOne;
	document.getElementById("bhaji_2").innerHTML = totalOptionTwo;
	document.getElementById("bhaji_total").innerHTML = (totalOptionOne + totalOptionTwo);
	document.getElementById("chapati_1").innerHTML = totalOptionOne * 2;
	document.getElementById("chapati_2").innerHTML = totalOptionTwo * 4;
	document.getElementById("chapati_total").innerHTML = ((totalOptionOne * 2) + (totalOptionTwo * 4));
	document.getElementById("rice_1").innerHTML = totalOptionOne * 2;
	document.getElementById("rice_2").innerHTML = 0;
	document.getElementById("rice_total").innerHTML = totalOptionOne * 2;
	document.getElementById("op1_total").innerHTML = totalOptionOne;
	document.getElementById("op2_total").innerHTML = totalOptionTwo;
	document.getElementById("kitchen_total").innerHTML = (totalOptionOne + totalOptionTwo);
	document.getElementById("op1_cost").innerHTML = "~ $" + totalOptionOne * 20;
	document.getElementById("op2_cost").innerHTML = "~ $" + totalOptionTwo * 24;
	document.getElementById("kitchen_cost").innerHTML = "$" + totalcost;




	// document.getElementById("num_orders").innerHTML = num_orders;
	// document.getElementById("num_one").innerHTML = totalOptionOne;
	// document.getElementById("num_two").innerHTML = totalOptionTwo;
	// document.getElementById("num_daal").innerHTML =(totalOptionOne + totalOptionTwo);
	// document.getElementById("num_bhaji").innerHTML = (totalOptionOne + totalOptionTwo);
	// document.getElementById("num_chapati").innerHTML = ((totalOptionOne * 2) + (totalOptionTwo * 4));
	// document.getElementById("num_rice").innerHTML = (totalOptionOne * 2);
}

function delivery(orders) {

	var num_orders = orders.length;
	var order_info = "";
	for (i = 0; i < num_orders; i++) {
		console.log(orders[i])
		//style='max-width: 18rem;'
		order_info += "<div class='card border-primary'><div class='card-header'>"
		// name

		order_info += orders[i].name['S'] + "</div><div class='card-body'><h5 class='card-title text-primary'>";
		//street address
		//order_info += orders[i].street['S'] + "<br>";
		//city/zip
		//order_info += orders[i].city['S'] + " " + orders[i].zipCode['N'] + "<br>";
		var payment = "";
		if (orders[i].paid["BOOL"] == false) {
			payment = "Unpaid, owes $" + orders[i].totalAmount['N'];
		}
		else {
			payment = "Paid $" + orders[i].totalAmount['N'];
		}
		order_info += payment + "</h5><p class='card-tex'>";

		one = parseInt(orders[i].mealOption1["N"])
		two = parseInt(orders[i].mealOption2["N"])

		order_info += "Option 1: " + one + "<br>";
		order_info += "Option 2: " + two + "<br><br>";

		order_info += orders[i].email['S'] + "<br>";
		order_info += orders[i].phone['S'] + "<br></p></div></div>";

	}
	document.getElementById("delivery").innerHTML = order_info;
}

$(document).ready(function(){
	const Url = 'https://o5yv1ecpk1.execute-api.us-west-2.amazonaws.com/dev/api/v1/meal/order';
	$.ajax({
		url: Url,
		type: "GET",
		datatype: 'json',
		success: function(res) {
			orders = res["result"];
			image();
			inventory(orders);
			delivery(orders);
		},
		error: function(error) {
			console.log("Error ${error}")
		}
	})
})