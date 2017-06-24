$('#UsernameInput').change(
  function(){
    
  var username = $(this).val();
  
  if (username.length != 0) {
    $.ajax({
      url: "/v/username/",
      data:{
            'username': username
           },
      dataType: 'json',
      
      success: function (data){
        $('.UsernameInputinfo').text(data['info']);
        $('.UsernameInputinfo').show();
        
        if (data['is_okey']){
          $('.username_block').removeClass('has-error').addClass('has-success');
          $('.UsernameInputinfo').removeClass('info_er').addClass('info_ok');
        }
        if (!data['is_okey']){
          $('.username_block').removeClass('has-success').addClass('has-error');
          $('.UsernameInputinfo').removeClass('info_ok').addClass('info_er');
        }
        
      }
    });
  }
  if (username.length == 0) {
    $('.username_block').removeClass('has-success').removeClass('has-error');
    $('.UsernameInputinfo').hide();
  }
});

$('#FirstnameInput').change(
  function(){
    var firstname = $(this).val();

    if (firstname.length > 2){
      $('.firstname_block').removeClass('has-error').addClass('has-success');
    }
    else{
      $('.firstname_block').removeClass('has-success').addClass('has-error');
    }
  });
    
$('#LastnameInput').change(
  function(){
    var lastname = $(this).val();

    if (lastname.length > 2){
      $('.lastname_block').removeClass('has-error').addClass('has-success');
    }
    else{
      $('.lastname_block').removeClass('has-success').addClass('has-error');
    }
  });

$('#EmailInput').change(
  function(){
    var email = $(this).val();

    if (email.length > 5){
      $('.email_block').removeClass('has-error').addClass('has-success');
    }
    else{
      $('.email_block').removeClass('has-success').addClass('has-error');
    }
  });


$('#LocationInput').change(
  function(){
    var location = $(this).val();

    if (location.length > 3){
      $('.location_block').removeClass('has-error').addClass('has-success');
    }
    else{
      $('.location_block').removeClass('has-success').addClass('has-error');
    }
  });

$('#SchoolInput').change(
  function(){
    var school = $(this).val();

    if (school.length > 2){
      $('.school_block').removeClass('has-error').addClass('has-success');
    }
    else{
      $('.school_block').removeClass('has-success').addClass('has-error');
    }
  });

$('#FormInput').change(
  function(){
    var form = $(this).val();

    if (form.length > 2){
      $('.form_block').removeClass('has-error').addClass('has-success');
    }
    else{
      $('.form_block').removeClass('has-success').addClass('has-error');
    }
  });

$('#PassInput1, #PassInput2').change(
  function(){
    var p1 = $('#PassInput1').val();
    var p2 = $('#PassInput2').val();
    
    if ((p1.length > 5 && p2.length > 5) &&
        (p1 == p2)){
        
        $('.pass1_block').removeClass('has-error').addClass('has-success');
        $('.pass2_block').removeClass('has-error').addClass('has-success');
    }
    else{
        $('.pass1_block').removeClass('has-success').addClass('has-error');
        $('.pass2_block').removeClass('has-success').addClass('has-error');
    }

  });

$('#BdateInput').change(
  function(){
    var form = $(this).val();

    if (form.length > 7){
      $('.birth_block').removeClass('has-error').addClass('has-success');
    }
    else{
      $('.birth_block').removeClass('has-success').addClass('has-error');
    }
  });
