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

fadeMax = {}

function postChannel() {
    var channels = $("#channels").val().map((v)=>{return parseInt(v)});
    keys = Object.keys(fadeMax);
    channels.forEach((v)=>{
        if (keys.indexOf("" + v) == -1) {
            fadeMax[v] = 255;
        }
    });
    API_post_json("./api/config/setChannel", {"channels": channels});
    updateRange(fadeMax);
}

function generateRange(index, value) {
    const template = '<label for="faderange{0}" class="form-label">CH {0} : <i>{1}</i></label>\
    <input type="range" class="form-range" id="faderange{0}" step="1" min="1" max="255" value="{1}" oninput=\'$("[for=" + this.id + "] > i").text($(this).val())\'>';
    return $(template.replace(/\{0\}/g, index).replace(/\{1\}/g, value));
}

function updateRange(map) {
    ranges = $("#ranges");
    ranges.empty();
    Object.keys(map).forEach((key)=>{
        elem = generateRange(key, map[key]);
        ranges.append(elem);
    });
}

function postFadeMax () {
    result = {}
    $("#ranges > input").each((i, e)=>{
        ch = e.id.replace("faderange", "");
        result[ch] = e.value;
    });
    API_post_json("./api/config/setTargetMax", {"fadeMaxs": result});
}

function loadConfig(Tags) {
    var channels = Tags.getInstance($("#channels")[0])
    jQuery.get("./api/config/target_max", (data)=>{
        fadeMax = data;
        jQuery.get("./api/config/channels", (data)=>{
            keys = Object.keys(fadeMax);
            $.each(data, (i, v)=>{
                channels.addItem(v);
                index = keys.indexOf("" + v);
                if (index == -1) {
                    fadeMax[v] = 255;
                }
                else {
                    delete keys[index];
                }
            });
            $.each(keys, (i,v)=>{
                delete fadeMax[v];
            });
            updateRange(fadeMax);
        });
    });
    jQuery.get("./api/config/interval", (data)=>{
        $("#fadespeed").val(data);
    });
    jQuery.get("./api/config/delay", (data)=>{
        $("#fadedelay").val(data);
    });
}