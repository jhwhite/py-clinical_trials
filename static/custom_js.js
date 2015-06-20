// function removeEmTag(){
//     var em = document.getElementsByTagName('em');

//     while(em.length) {
//         var parent = em[ 0 ].parentNode;
//         while( em[ 0 ].firstChild ) {
//             parent.insertBefore(  em[ 0 ].firstChild, em[ 0 ] );
//         }
//          parent.removeChild( em[ 0 ] );
//     }
// }

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
