/**
 * Show sidebar menu on the right
 */
function menu_toggle(){
    document.getElementById("main-container").classList.toggle("toggled");
};

/**
 * Hide navigation menu for small viewports, when it is again enlarged
 */
function hide_navigation(){
    const navbar_expand_xl = "1200px";
    var mq = window.matchMedia( "(min-width: " + navbar_expand_xl + ")" );
    if (mq.matches)
        document.getElementById("navigation").classList.remove("show");
};
