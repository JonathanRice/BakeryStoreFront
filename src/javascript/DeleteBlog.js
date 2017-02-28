$(document).ready(function(){
	$("[warning]").click(function() {		
		return confirm($(this).attr("warning"));
	});  
});