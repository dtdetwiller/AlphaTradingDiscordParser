$(document).ready(function() {

   $( ".status" ).each(function(){
       var value = parseInt( $( this ).html() );
       if ( value < 0 )
       {
           $( this ).parent().css('background-color', 'red');
       }
   });
});