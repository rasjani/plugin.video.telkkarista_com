
function toSourceTime(localtime) {
    var output = new Date(localtime);
    output.setHours(output.getHours() + timezoneOffset);
    return new Date(output);
}


function fixDate(d) {
    if(!client.settings.timeOffset || client.settings.timeOffset == "source") {
        return toSourceTime(d);
    } else {
        return d;
    }
}



function epgLang(data) {
    var lang = null, otherLang = null;
    if(!client.settings.epgLang || client.settings.epgLang == 'fi') {
        lang = 'fi';
        otherLang = 'sv';
    } else {
        lang = 'sv';
        otherLang = 'fi';
    }
    return data[lang]?data[lang]:data[otherLang];    
}

function visibleName(name) {
    var visibleName = null;
    streams.forEach(function(stream) {
        if(stream.name == name) {
            visibleName = stream.visibleName;
            return false;
        }
    });
    return visibleName||name;
}

function renderTime(time) {
    var time = new Date.fromISO(time);
    // local / origin timezone stuff..
    time = fixDate(time);
    return ( ( time.getHours() < 10 ) ? '0' + time.getHours() : time.getHours() ) + ':' + ( ( time.getMinutes() < 10 ) ? '0' + time.getMinutes() : time.getMinutes() );    
}



