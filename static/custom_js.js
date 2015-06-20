function toggleEmClass() {
    $( "em" ).toggleClass( "highlight" );

}

$(document).ready(function(){
    $('#search-help').hide();
    $(".show-help").click(function(){
        $("div").slideDown();
    });
    $(".btn2").click(function(){
        $("p").slideDown();
    });


});
