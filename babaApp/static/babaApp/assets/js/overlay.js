
function overlay() {
    document.getElementById("test_element").innerHTML = "test element: " + (Math.random() * 100).toString();

    document.getElementById('overlay').style.visibility = 'visible'

//    $("<div id='overlay' style='margin: 30px 0px 0px 0px'>" +
//       "<p> Enter new strategy name: </p>" +
//       "<form action='' method='POST'>" +
//         "{% csrf_token %}" +
//         "<input type='text'>" +
//       "</form>" +
//       "<button onclick='removeOverlay()' style='width:200px;height:40px;margin:40px 0px 0px 0px'>CANCEL</button>" +
//       "</div>"
//    ).css({
//        "position": "absolute",
//        "top": "20%",
//        "left": "30%",
//        "width": "40%",
//        "height": "275px",
//        "background-color": "rgba(0,0,0,.85)",
//        "z-index": 100,
//        "vertical-align": "middle",
//        "text-align": "center",
//        "color": "#fff",
//        "font-size": "30px",
//        "padding": 10,
//    }).appendTo("body");
}

function removeOverlay() {
    document.getElementById('overlay').style.visibility = 'hidden'
}
//
//$("body").click(function(){
//  removeOverlay()
////  $(".popup").fadeOut().removeClass("active");
//});
//
//// Prevent events from getting pass .popup
//$("#overlay").click(function(e){
//  e.stopPropagation();
//});