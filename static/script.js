$(document).ready(function() {
	$("#login").click(funtion(){
		$("#message").show();
	});	
	$(".show").click(function(){
		$(this).next().slideToggle("slow");
	});
});