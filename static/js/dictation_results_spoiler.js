jQuery(document).ready(function(){
		jQuery('.dictation-text').hide();
		jQuery('.dictation-name').click(function(){
			jQuery(this).toggleClass("folded").toggleClass("unfolded").next().slideToggle()
		});
});

jQuery(document).ready(function(){
  
        jQuery('.dictation-text-checked').show();
		jQuery('.dictation-name-checked').click(function(){
			jQuery(this).toggleClass("unfolded").toggleClass("folded").next().slideToggle()
		});
});