var timeoutInMiliseconds = 120000;
var timerId;
var el = document.querySelector("#homepage");
var el2 = document.querySelector("#start");
var el3 = document.querySelector("#welcome");

if (el2 != null) {
    el2.addEventListener("click", function () {
        el.style.display = '';
        el3.parentNode.removeChild(el3);
    });
}

function startTimer() {
    timerId = window.setTimeout(goHome, timeoutInMiliseconds)
}
function resetTimer() {
    window.clearTimeout(timerId)
    startTimer();
}
function goHome() {
    window.location.replace("/");
}
function setupTimers() {
    document.addEventListener("mousemove", resetTimer, false);
    document.addEventListener("mousedown", resetTimer, false);
    document.addEventListener("keypress", resetTimer, false);
    document.addEventListener("touchmove", resetTimer, false);
    startTimer();
}
function ready(callbackFunc) {
    if (document.readyState !== 'loading') {
        callbackFunc();
    } else if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', callbackFunc);
    } else {
        document.attachEvent('onreadystatechange', function () {
            if (document.readyState === 'complete') {
                callbackFunc();
            }
        });
    }
}

ready(function () {
    setupTimers();
});
