/**
 * Compare a password with a confirm password and eventually color red 
 * @param pswd_id Password id
 * @param conf_id Confirm password id
 * @return Bool value whether the passwords are the same
 */
function compare_passwords(pswd_id, conf_id) {
    var pswd = document.getElementById(pswd_id);
    var conf_pswd = document.getElementById(conf_id);

    if(pswd.value != conf_pswd.value){
        var warn_col = "red";
        pswd.style.color = warn_col;
        conf_pswd.style.color = warn_col;
        return false;
    }

    pswd.style.color = "black";
    conf_pswd.style.color = "black";
    return true;
}

/**
 * Validate the form values before submit
 * @param pswd_id Password id
 * @param conf_id Confirm password id
 * @return Bool true if ok, false if there are errors
 */
function validate(pswd_id, conf_id) {
    var pswd = document.getElementById(pswd_id);
    var conf_pswd = document.getElementById(conf_id);

    if(pswd.value == "" || conf_pswd.value == ""){
        alert("Error: Invalid password!");
        return false;
    }
    else if(compare_passwords(pswd_id, conf_id) == false){
        alert("Error: Passwords do not match!");
        return false;
    }
    return true;
}