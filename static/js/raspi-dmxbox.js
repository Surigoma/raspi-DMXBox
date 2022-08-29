function API_get(path) {
    jQuery.get("./api/" + path);
}
function API_post(path, object={}) {
    jQuery.post(path, object);
}
function API_post_json(path, object={}) {
    jQuery.ajax(path, {
        method: "POST",
        data: JSON.stringify(object),
        contentType : "application/json"
    });
}
function postChannel() {
    var channels = $("#channels").val().map((v)=>{return parseInt(v)});
    API_post_json("./api/config/setChannel", {"channels": channels})
}