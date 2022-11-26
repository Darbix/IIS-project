/**
 * Process profile edit enable/disable content, send/reset input values 
 * @param btn_id Edit/Save button id
 * @param field_id Field id that disables a content
 * @param form_id Form id
 * @param cancel_id Cancel button id
 * @param action if 'SEND', the form is sent, else it is reset
 */
function toggle_edit(btn_id, field_id, form_id, cancel_id, action){
    var field = document.getElementById(field_id);
    var btn = document.getElementById(btn_id);
    var cancel = document.getElementById(cancel_id);
    var form = document.getElementById(form_id);

    if(field.disabled == true){
        field.disabled = false;
        btn.classList.toggle("fa-pen-to-square")
        btn.classList.toggle("fa-check")

        cancel.hidden = false;
    }
    else{
        btn.classList.toggle("fa-pen-to-square")
        btn.classList.toggle("fa-check")

        cancel.hidden = true;
        
        if(action == "SEND")
            form.submit();
        else
            form.reset();
            
        field.disabled = true;
    }
}

/**
 * Load the uploaded image directly to a profile view
 * @param event Event
 * @param img_id Image id
 */
function load_img(event, img_id){
    var image = document.getElementById(img_id);
    image.src = URL.createObjectURL(event.target.files[0]);
};

/**
 * Show password
 * @param id Password input id
 */
function show_password(id){
    var pswd = document.getElementById(id);
    if (pswd.type === "password")
        pswd.type = "text";
    else
        pswd.type = "password";
}