// include the client
var client =  new libStreamingClient('telkkarista.com',true);
var sourceTimezone = +3;
var myTimezone = -(new Date().getTimezoneOffset() / 60);
var timezoneOffset = sourceTimezone - myTimezone;
var page = 'login';
$('.loader').hide();

jQuery(document).ready(function ($) {
    //Live stream show actions
    $(function () {
        var streamTV = $('.tv');

        streamTV.on('click', function () {
            if ($(this).data('activated') == 'yes') {
                return false;
            }

            if (streamTV.hasClass('active')) {
                streamTV.removeClass('active').find('.tv-actions').slideUp(300);
                streamTV.data('activated', 'no');
            }

            $(this).data('activated', 'yes');
            $(this).find('.tv-actions').slideDown(300);
            $(this).addClass('active');
        });
    });


    //Open video player
    $(function () {
        var vpHeight = $('.video-player').height(),
            wWidth = $(window).width(),
            actions = $('#actions'),
            playerInfo = $('#video-player-info'),
            openInfoEl = $('#action-open-info'),
            closeInfoEl = $('#action-close-info'),
            closePlayerEl = $('#action-close');

        $(window).resize(function () {
            vpHeight = $('.video-player').height();
            wWidth = $(window).width();

            $('.page.player-opened').css('marginTop', vpHeight + 50);

            if(wWidth > 480 && wWidth < 768) {
                $('.video-player-info.info-opened').css('height', vpHeight);
                $('.video-player-info.info-closed').css('height', 0);
                if (playerInfo.hasClass('info-opened')) {
                    openInfoEl.css('display', 'none');
                    closeInfoEl.show();
                    closePlayerEl.hide();
                } else {
                    openInfoEl.css('display', 'block');
                }
            } else {
                $('.video-player-info.info-opened').css('height', 'auto');
                openInfoEl.css('display', 'none');
                closeInfoEl.hide();
                closePlayerEl.show();
            }
        });

        //Open video pLayer
        $('.action-play').click(function () {
            openInfoEl.hide();

            $('.video-player')
                .slideDown(500, function(){
                    closePlayerEl.fadeIn(300);

                    if(wWidth > 480 && wWidth < 768) {
                        openInfoEl.fadeIn(300);
                    }
                })
                .addClass('player-opened');

            $('.page')
                .animate({
                    'marginTop' : vpHeight + 50
                }, 500)
                .addClass('player-opened');
        });

        //Close video player
        closePlayerEl.click(function () {
            $('.video-player')
                .slideUp(500)
                .removeClass('player-opened');

            closePlayerEl.hide(0);
            openInfoEl.hide(0);

            $('.page')
                .animate({
                    'marginTop' : 50
                }, 500)
                .removeClass('player-opened');

            playerInfo.removeClass('info-opened').addClass('info-closed');
        });

        //Show video info in tablet view
        openInfoEl.on('click', function () {
            actions.addClass('info-opened');

            openInfoEl.fadeOut(300);
            closePlayerEl.fadeOut(300);

            $('.video-player-info')
                .animate({
                    'height' : vpHeight
                }, 500, function () {
                        $(this).removeClass('info-closed').addClass('info-opened');
                        closeInfoEl.fadeIn(300);
                    });
        });

        //Hide video info in tablet view
        closeInfoEl.on('click', function () {
            actions.removeClass('info-opened');

            $(this).fadeOut();
            closePlayerEl.fadeIn(300);
            openInfoEl.fadeIn(300);

            $('.video-player-info')
                .animate({
                    'height' : 0
                }, 500)
                .removeClass('info-opened').addClass('info-closed');

        });
    });

    //////////////////////////
    // chuck norris was here//
    //////////////////////////

    // variables to store stuff in
    var clientReady = false;
    var streams = [];

    // setup our listeners
    client.on('loginRequired', function() { showLogin() });
    client.on('sessionTimeout', function() { showLogin('timeout'); });
    client.on('ready', function() { clientReady = true; });
    client.on('speedtestStart', function(data) { speedtestStart(data); });
    client.on('speedtestDone', function(servers) { speedtestDone(servers); });
    client.on('speedtestProgress', function(result) { speedtestProgress(result); });
    client.on('error', function() { /* ignore errors for now */ });

    // init client
    client.init();
});

function renderPage(template, data) {
    $('#page').html(Handlebars.getTemplate(template)(data));
}

function renderPart(id, template, data) {
    $('#'+id).html(Handlebars.getTemplate(template)(data));
}

function appendPage(template, data) {
    $('#page').append(Handlebars.getTemplate(template)(data));
}

function renderMenu(data) {
    $('#navbar').html(Handlebars.getTemplate('menu')(data));
}

var sessionId = null;

function showLogin(from, login, password) {
    $('#nav').html('');
    renderPage('login');
    if(login) $('#login-user').val(login);
    if(password) $('#login-pass').val(password);

    $('#loginform').submit(function(e) {
        e.preventDefault();

        client.user.login($('#login-user').val(), $('#login-pass').val())
            .then(function(sess) {
                // on login success we get the session id, we can store this or ignore it..
                sessionId = sess;
            })
            .error(function(err) {
                switch(err) {
                    case 'user_not_found':
                        $('#login-error').html('<b>Error!</b> User not found!').show();
                    break;
                    case 'invalid_password':
                        $('#login-error').html('<b>Error!</b> Invalid password!').show();
                    break;
                    case 'invalid_request':
                        $('#login-error').html('<b>Error!</b> Invalid request, check that you filled both email and password!').show();
                    break;
                    default:
                        $('#login-error').html(err).show();
                    break;
                }
            });

        return false;
    });
}

function openPlayer(pid, playlist, stream) {
    if(pid) {
        $('#video-container').html(Handlebars.getTemplate('videoPlayer')({pid: pid}));
    } else {
        $('#video-container').html(Handlebars.getTemplate('videoPlayer')({playlist: playlist, stream: stream}));
    }
}


function showRegister() {
    $('#nav').html('');
    renderPage('register');
    $('#registerform').submit(function(e) {
        e.preventDefault();

        client.user.register($('#register-user').val(), $('#register-pass').val())
            .then(function(status) {
                showLogin(false, $('#register-user').val(), $('#register-pass').val());
                console.log(status);
            })
            .error(function(err) {
                console.log(err);
            });
    });
}

function speedtestStart(data) {
    if(page == 'settings') {
        // hack to not change page, lets clear current speedtest results
        $('.speedtest-result').css('background-color', '#ffffff');
        $('.speedtest-mbit').html('');
        $('.serverSelect').hide();
    } else {
        renderPage('speedtests', data);
        $('#speedtests-ongoing').show();
        clearInterval(speedtestTimeout);
    }
}


function speedtestProgress(result) {
    if(result.server.host) {
        $('#speed-' + strHash(result.server.host)).html(result.server.speedtest.mbit.toFixed(2) + 'mbps');
    }
}

var speedtestTimeout = null, speedtestTimeoutCounter = 10;

function speedtestDone(result) {
    $('.serverSelect').show();
    $('#speedtests-ongoing').hide();
    $('#speedtests-done').show();
    speedtestTimeoutCounter = 10;
    $('#speedtest-timeout').html(speedtestTimeoutCounter);

    var first = 1;

    result.forEach(function(server) {
        if(first) {
            $('#speed-' + strHash(server.host)).parent().parent().css('background-color', '#b8ea8d');
            first=0;
        }
        $('#speed-' + strHash(server.host)).html(server.speedtest.mbit.toFixed(2) + 'mbps');
    });

    speedtestTimeout = setInterval(function() {
        speedtestTimeoutCounter--;
        $('#speedtest-timeout').html(speedtestTimeoutCounter);
        if(speedtestTimeoutCounter == 0) {
            showStreams();
            clearInterval(speedtestTimeout);
        }
    }, 1000);
}

function selectServer(host, page) {
    var servers = client.cacheServers;
    var outServers = [];
    var ourServer = null;
    servers.forEach(function(server) {
        if(server.host == host) {
            ourServer = server;
        } else {
            outServers.push(server);
        }
    });
    outServers.reverse();
    outServers.push(ourServer);
    outServers.reverse();
    client.cacheServers = outServers;

    if(page == 'streams') showStreams();
    else if(page == 'settings') showSettings();
}

function showStreams() {
    clearTimeout(speedtestTimeout);
    page = 'streams';
    renderMenu({page: 'streams'});

    client.streams.get()
        .then(function(_streams) {
            streams = _streams;
            renderPage('streams', streams);
        });
}


var epgDate = null;
function showEPG() {
    $('.loader').show();
    page = 'epg';
    renderMenu({page: 'epg'});

    var offset = client.settings.timeOffset?client.settings.timeOffset:'source';

    if(!epgDate) {
        epgDate = new Date();
    }
    var start = new Date(epgDate);
    var end = new Date(epgDate);
    start.setHours(0,0,0,0);
    end.setHours(23,59,59,999);

    if(offset == 'source') {
        start.setHours(start.getHours()-timezoneOffset);
        end.setHours(end.getHours()-timezoneOffset);
    }

    client.epg.range(start, end)
        .then(function(data) {
            var outData = {};

            Object.keys(data).forEach(function(name) {
                outData[name] = [];
                for(var i=0; i < 24; i++) {
                    outData[name][i]=[];
                }
                data[name].forEach(function(epgObject) {
                    var start = new Date(epgObject.start);
                    start = fixDate(start);
                    outData[name][start.getHours()].push(epgObject);
                });
            });

            var outOrdered = [];

            streams.forEach(function(stream) {
                outOrdered.push({name: stream.name, hours: outData[stream.name]});
            });

            delete outData;
            delete data;

            renderPage('epg', {streams: streams, epg: outOrdered});
            initEPGUI();
            $('.loader').hide();
        })
        .error(function(err) {
            console.log(err);
            $('.loader').hide();
        });
}

function showSettings() {
    page = 'settings';
    renderMenu({page: 'settings'});
    var settings = client.settings;
    if(!client.settings.timeOffset) {
        client.settings.timeOffset = 'local';
        client.user.setSetting('timeOffset', 'local')
            .then(function() {})
            .error(function(err) {
                console.log(err);
            });
    }
    if(!client.settings.epgLang) {
        client.settings.epgLang = 'fi';
        client.user.setSetting('epgLang', 'fi')
            .then(function(){})
            .error(function(err) {
                console.log(err);
            });
    }
    settings.servers = client.cacheServers;

    renderPage('settings',settings);

    var first = true;
    settings.servers.forEach(function(server) {
        if(first) {
            $('#speed-' + strHash(server.host)).parent().parent().css('background-color', '#b8ea8d');
            first = false;
        }
        $('#speed-' + strHash(server.host)).html(server.speedtest.mbit.toFixed(2) + 'mbps');
    });

}

function toSourceTime(localtime) {
    var output = new Date(localtime);
    output.setHours(output.getHours() + timezoneOffset);
    return new Date(output);
}

function showFAQ() {
    page = 'faq';
    renderMenu({page: 'faq'});
    renderPage('faq');
}

function changeTimeOffset(offset) {
    client.settings.timeOffset = offset;
    client.user.setSetting('timeOffset', offset)
        .then(function() {
            // here you could show a fade in/out "ok" mark or something..
            var offsetString = '';
            if(offset == 'local') offsetString = 'Local';
            else offsetString = 'Source';
            $('#timeOffset').css('background-color', '#b8ea8d').val(offsetString);
            setTimeout(function() {
                $('#timeOffset').css('background-color', '#FFFFFF');
            },2000);
        })
        .error(function(err) {
            console.log(err);
        });
}

function changeEPGLang(lang) {
    client.settings.epgLang = lang;
    client.user.setSetting('epgLang', lang)
        .then(function() {
            // here you could show a fade in/out "ok" mark or something..
            var langString = '';
            if(lang == 'fi') langString = 'Finnish';
            else langString = 'Swedish';
            $('#epgLang').css('background-color', '#b8ea8d').val(langString);
            setTimeout(function() {
                $('#epgLang').css('background-color', '#FFFFFF');
            },2000);
        })
        .error(function(err) {
            console.log(err);
        });
}

function fixDate(d) {
    if(!client.settings.timeOffset || client.settings.timeOffset == "source") {
        return toSourceTime(d);
    } else {
        return d;
    }
}


function showEPGInfo(pid) {
    client.epg.info(pid)
        .then(function(data) {
            data.downloads = {};
            if(data.downloadFormats) {
                Object.keys(data.downloadFormats).forEach(function(format) {
                    data.downloadFormats[format].forEach(function(quality) {
                        if(format == 'mp4') {
                            $('#mp4-' + pid).append('<a href="' + client.vod.getDownload(data, format, quality) +'" class="btn btn-xs btn-default" data-toggle="tooltip" data-placement="top" title="">' + quality + '</a>\n');
                        }
                    });
                });

            }

            $('#info-' + pid).html(epgLang(data['sub-title']));
        })
        .error(function(code) {
            console.log(code);
        });
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


function initEPGUI() {
    //Datepicker
    $('#date-picker').datepicker({
        format: 'dd.mm.yyyy',
        autoclose: true,
        container: '#date-picker',
        orientation: 'top left',
        weekStart: 1,
        todayHighlight: true
    });

    //Datepicker current date
    if(epgDate) {
        $('#date').val(moment(epgDate).format('DD.MM.YYYY'));
        $('#date-picker').datepicker('update', moment(epgDate).format('DD.MM.YYYY'));
    } else {
        $('#date').val(moment().format('DD.MM.YYYY'));
        $('#date-picker').datepicker('update', moment().format('DD.MM.YYYY'));
    }


    var loadingEpg = null;
    $('#date').on('change', function() {
        var list = this.value.split('.');
        epgDate = new Date(list[2], list[1]-1, list[0]);

        // for some reason this fires 3 times so timeout should fix that..
        clearTimeout(loadingEpg);
        loadingEpg = setTimeout(showEPG, 300);
    });


    //EPG Slider
    var epgSliderEl = $('#epg-slider'),
        epgSlider = epgSliderEl.owlCarousel({
            items: 5,
            margin: 16,
            loop: false,
            pullDrag: false,
            dragEndSpeed: 300,
            dots: true,
            dotsEach: 1,
            nav: false,
            responsiveRefreshRate: 50,
            responsive:{
                0:{
                    items:1
                },
                500:{
                    items:2
                },
                768:{
                    items:3
                },
                1000:{
                    items:4
                },
                1400:{
                    items:5
                }
            },
        });

    $('#epg-nav-next').click(function() {
        epgSlider.trigger('next.owl.carousel');
    });

    $('#epg-nav-prev').click(function() {
        epgSlider.trigger('prev.owl.carousel');
    });

    //Enable Tooltips
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    //Channel click
    $(function () {
        var channelTab = $('.epg-channel'),
            channelSlides = $('.epg-slide'),
            channelIndex;

        channelSlides.each(function () {
            if ($(this).parent().hasClass('active')) {
                var channelIndex = $(this).attr('data-slide-index');

                channelTab.each(function(){
                    if(channelIndex == $(this).attr('data-slide-index')) {
                        $(this).addClass('active');
                    }
                });
            }
        });

        epgSlider.on('resized.owl.carousel', function(e) {
            channelSlides.each(function () {
                if ($(this).parent('.owl-item').hasClass('active')) {
                    channelIndex = $(this).attr('data-slide-index');
                    channelTab.each(function(){
                        if(channelIndex == $(this).attr('data-slide-index')) {
                            $(this).addClass('active');
                        }
                    });
                } else {
                    channelIndex = $(this).attr('data-slide-index');
                    channelTab.each(function(){
                        if(channelIndex == $(this).attr('data-slide-index')) {
                            $(this).removeClass('active');
                        }
                    });
                }
            });
        });

        epgSlider.on('translated.owl.carousel', function(e) {
            channelSlides.each(function () {
                if ($(this).parent('.owl-item').hasClass('active')) {
                    channelIndex = $(this).attr('data-slide-index');
                    channelTab.each(function(){
                        if(channelIndex == $(this).attr('data-slide-index')) {
                            $(this).addClass('active');
                        }
                    });
                } else {
                    channelIndex = $(this).attr('data-slide-index');
                    channelTab.each(function(){
                        if(channelIndex == $(this).attr('data-slide-index')) {
                             $(this).removeClass('active');
                        }
                    });
                }
            });
        });

        channelTab.on('click', function() {
            var tabIndex = $(this).attr('data-slide-index');
            epgSlider.trigger('to.owl.carousel', [tabIndex, 500]);
        });
    });

    //Epg show info
    $(function () {
        var epg = $('.epg-content-program');
        $('.epg-actions-download').click(function(e) {
            e.stopPropagation();
        });

        epg.on('click', function (e) {
            if ($(this).data('activated') == 'yes') {
                return false;
            }

            if (epg.hasClass('active')) {
                epg.removeClass('active').find('.epg-actions').slideUp(300);
                epg.data('activated', 'no');
            }

            $(this).data('activated', 'yes');
            $(this).find('.epg-actions').slideDown(300);
            $(this).addClass('active');
        });
    });

    setTimeout(function(){
        for(var i = 0; i < 24; i++) {
            var hourHeight = 0,
                hourEl = $('.hour-'+i);

            hourEl.each(function(){
                var elHeight = $(this).outerHeight();
                if (elHeight > hourHeight) {
                    hourHeight = elHeight;
                }
            });

            hourEl.css('min-height', hourHeight);
        }
    }, 1000);

    //Fixed position for EPG channel titles
    $(window).on('scroll', function () {
        var offset = $(document).scrollTop();
        $('.epg-channel-title').stop().css('top', offset);
    });

    //Fix EPG slider margin in mobile
    if ($(window).width() < 768) {
        $('#epg-slider').css('marginTop', $('.epg-nav-container').outerHeight() + 110)
    }

    //Horizontal Scroll
    var mousewheelMove = null, scrollPos = 0, mousewheelReset = null;
    epgSliderEl.on('mousewheel', function(event) {
        scrollPos += event.deltaX;
        if(scrollPos > 100) {
            scrollPos = 0;
            epgSlider.trigger('next.owl.carousel');
        }
        if(scrollPos < -100) {
            scrollPos = 0;
            epgSlider.trigger('prev.owl.carousel');
        }
        clearTimeout(mousewheelReset);
        mousewheelReset = setTimeout(function(){
            scrollPos = 0;
        }, 1000);


/*        var sensitivity = 20, jitter = 50;
        if (event.deltaX > sensitivity) {
            clearTimeout(mousewheelMove);
            mousewheelMove = setTimeout(function() {
                epgSlider.trigger('next.owl.carousel');
            },jitter);
        } else if (event.deltaX < -sensitivity) {
            clearTimeout(mousewheelMove);
            mousewheelMove = setTimeout(function() {
                epgSlider.trigger('prev.owl.carousel');
            },jitter);
        }*/
    });
}
