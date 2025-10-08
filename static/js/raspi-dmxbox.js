function API_get(path) {
    jQuery.get("./api/" + path);
}
function API_get_param(path, param) {
    jQuery.get("./api/" + path, param);
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
fadeNormal = []
fadeAdd = []

function postChannel() {
    var channels = $("#channels").val().map((v)=>{return parseInt(v)});
    keys = Object.keys(fadeMax);
    channels.forEach((v)=>{
        if (keys.indexOf("" + v) == -1) {
            fadeMax[v] = 255;
        }
    });
    API_post_json("./api/config/setChannel", {"channels": channels});
    updateRange();
}

function postAddChannel() {
    var channels = $("#additional_ch").val().map((v)=>{return parseInt(v)});
    keys = Object.keys(fadeMax);
    channels.forEach((v)=>{
        if (keys.indexOf("" + v) == -1) {
            fadeMax[v] = 255;
        }
    });
    API_post_json("./api/config/setAddChannel", {"channels": channels});
    updateRange();
}

function generateRange(index, value) {
    const template = '<label for="faderange{0}" class="form-label">CH {0} : <i>{1}</i></label>\
    <input type="range" class="form-range" id="faderange{0}" step="1" min="1" max="255" value="{1}" oninput=\'$("[for=" + this.id + "] > i").text($(this).val())\'>';
    return $(template.replace(/\{0\}/g, index).replace(/\{1\}/g, value));
}

function generateWCTitle(w, d) {
    return "W:" + Math.round(w * 100) + "% D:"+ Math.round(d * 100) + "%";
}

function updateWCRange(elm) {
    var ch = parseInt(elm.id.replace("_w", "").replace("_d", "").replace("fadewcrange", ""));
    var label_elm = $("[for=faderange" + ch + "] > i");
    var w_v = $("#fadewcrange" + ch + "_w")[0].value;
    var d_v = $("#fadewcrange" + ch + "_d")[0].value;
    label_elm.text(generateWCTitle(w_v, d_v));
    const ch1 = Math.round(d_v * w_v * 255);
    const ch0 = Math.round(255 * d_v - ch1);
    $("#faderange" + ch)[0].value = ch0;
    $("#faderange" + (ch + 1))[0].value = ch1;
}

function generateWCRange(index, value) {
    let wc = (value[0] / (value[0] + value[1]));
    if (isNaN(wc)) { wc = 0.5; }
    let dim = Math.max(value[0], value[1]) / 255;
    const template = '<label for="faderange{0_0}" class="form-label">CH {0_0}-{0_2} : <i>{3}</i></label>\
    <input type="hidden" id="faderange{0_0}" value="{2_0}"/> \
    <input type="hidden" id="faderange{0_1}" value="{2_1}"/> \
    <input type="hidden" id="faderange{0_2}" value="0" /> \
    <input type="range" class="form-range" id="fadewcrange{0_0}_w" step="0.01" min="0" max="1" value="{1}" oninput=\'updateWCRange(this);\'> \
    <input type="range" class="form-range" id="fadewcrange{0_0}_d" step="0.01" min="0" max="1" value="{2}" oninput=\'updateWCRange(this);\'>';
    return $(template.replace(/\{0_0\}/g, index).replace(/\{0_1\}/g, index + 1).replace(/\{0_2\}/g, index + 2).replace(/\{1\}/g, wc).replace(/\{2\}/g, dim).replace(/\{2_0\}/g, value[0]).replace(/\{2_1\}/g, value[1]).replace(/\{3\}/g, generateWCTitle(wc, dim)));
}

function updateRange() {
    ranges = $("#ranges");
    ranges.empty();
    fadeNormal.forEach((key)=>{
        ary = [fadeMax[key], fadeMax[key + 1], fadeMax[key + 2]]
        elem = generateWCRange(key, ary);
        ranges.append(elem);
    });
    fadeAdd.forEach((key)=>{
        elem = generateRange(key, fadeMax[key]);
        ranges.append(elem);
    });
}

function postFadeMax () {
    result = {}
    $("#ranges > input").each((i, e)=>{
        ch = e.id.replace("faderange", "");
        if (isNaN(parseInt(ch))) { return }
        result[ch] = e.value;
    });
    API_post_json("./api/config/setTargetMax", {"fadeMaxs": result});
}

function loadConfig(Tags) {
    var channels = Tags.getInstance($("#channels")[0])
    var add_channels = Tags.getInstance($("#additional_ch")[0])
    jQuery.get("./api/config/target_max", (data)=>{
        fadeMax = data;
        jQuery.get("./api/config/channels", (data_c)=>{
            jQuery.get("./api/config/add_channels", (data_ac)=>{
                fadeNormal = data_c;
                fadeAdd = data_ac;
                keys = Object.keys(fadeMax);
                $.each(data_c, (i, v)=>{
                    channels.addItem(v);
                    index = keys.indexOf("" + v);
                    if (index == -1) {
                        fadeMax[v] = 255;
                    }
                    else {
                        [0, 1, 2].forEach((i)=>{
                            if (keys[index + i] === undefined) { return; }
                            delete keys[index + i];
                        });
                    }
                });
                $.each(data_ac, (i, v)=>{
                    add_channels.addItem(v);
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
            })
        });
    });
    jQuery.get("./api/config/interval", (data)=>{
        $("#fadespeed").val(data);
    });
    jQuery.get("./api/config/delay", (data)=>{
        $("#fadedelay").val(data);
    });
}

function loadIndex() {
    jQuery.get("./api/config/ignore_remote", (data)=>{
        $("#ignoreRemote").prop("checked", data);
    });
}