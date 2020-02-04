$(document).ready(function(){

      $(".glyphicon").on('click',function(){
        if($(".navbar1").hasClass("navbar1")) {
            $(".navbar1").removeClass("navbar1");
        } else {
            $(".topnav").addClass("navbar1");
        }

        if($(".topnav2").hasClass("navbar2")) {
            $(".topnav2").removeClass("navbar2");
        } else {
            $(".topnav2").addClass("navbar2");
        }

      });
//          $(".topnav").hide();
//    $(".glyphicon").on("click", function () {
//        var txt = $(".content").is(':visible') ? 'Read More' : 'Read Less';
//        $(".show_hide").text(txt);
//        $(this).next('.content').slideToggle(200);
//        if ($(".topnav").is(":visible")) {
//            $(".topnav").css("display", "none");
//        }
//    });
});