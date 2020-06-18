var el = document.querySelector("#homepage");
var el2 = document.querySelector("#start");
var el3 = document.querySelector("#welcome");

if (el2 != null) {
    el2.addEventListener("click", function () {

        el.style.display = '';
        el3.parentNode.removeChild(el3);



    });
}




