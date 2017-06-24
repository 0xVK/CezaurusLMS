jQuery(document).ready(function(){
		jQuery('.message-answer-fm').hide();
		jQuery('.btn-answer').click(function(){
			$('.message-answer-fm').toggleClass("folded").toggleClass("unfolded").slideToggle()
		});
});


$('#confirm-send-btn').click(function(){
  document.forms["send-message-fm"].submit();
});
