var libStreamingClient = function(host, debug){
	var debug = debug?true:false;

	// if we are running the client on correct domain, disable debugging
	if(window.location.host.indexOf(host) != -1) debug = false;

	// Some browsers apparently dont have console?!?
	if(debug) {
		if(!console) console = {};
		if(!console.log) {
			console.log = function() {};
		}
	}

	/*
	 * This is our client object where all other functions are loaded to
	 */
	var client = {
		apiEndpoint: 'https://api.' + host,
		loginService: 'https://login.' + host,
		versionString: 'libStreamingClient/0.1.5 20150313 (friday the 13th edition)',
		apiVersion: '1',
		storage: null,
		user: {},
		streams: {},
		epg: {},
		vod: {},
		cache: {},
		news: {},
		time: {},
		documentation: {},
		cacheServers: [],
		settings: null,
		suckyBrowser: false
	};

	// Since IE8 & IE9 does not support CORS we need to throw an error so we can do tricks
	if(navigator.appName.indexOf("Internet Explorer")!=-1) {
		//if(navigator.appVersion.indexOf("MSIE 1") == -1) { // IE10+ are ok
		// Who was I kidding, IE is never OK, back to the proxy for "modern" IE browsers as well..
			sendToDogHouse();
		//}
	} else if(navigator.appName.indexOf("Netscape") != -1 && navigator.userAgent.indexOf('Trident') != -1) {
		// IE11 is trying to be sneaky.. Still send them to doghouse since cors, wtf? get it right!
		sendToDogHouse();
	}
	//sendToDogHouse();

	function sendToDogHouse() {
		if(window.location.host.indexOf(host) == -1) {
			if(!confirm('You are loading this script from untrusted location, do you want to continue?')) {
				throw new Error('Untrusted');
			}
		}
		client.suckyBrowser = true;
		client.apiEndpoint = 'https://' + window.location.host + '/corsproxy';
	}
	
	/*
	 * Storage handler
	 */
	if(window.localStorage) {
		localStorage['client'] = client.versionString;
		if(localStorage.client ==  client.versionString) {

			client.storage = {
				get: function(key) { return localStorage[key]?JSON.parse(localStorage[key]):null; },
				set: function(key, value) { value = JSON.stringify(value); localStorage[key] = value; return localStorage[key]==value },
				del: function(key) { delete localStorage[key]; }	
			};
		}
	}

	/*
	 * Localstorage failed, fall back to cookies
	 */
	if(!client.storage && navigator.cookieEnabled) {
		client.storage = {
			get: function(key) {
				key+='=';
				var cookies = document.cookie.split(';');
				for(var i=0; i <cookies.length; i++) {
					var cookie = cookies[i].trim();
					if(cookie.indexOf(key) == 0) return JSON.parse(cookie.substring(key.length,cookie.length));
				}
			},
			set: function(key, value) { document.cookie = key + "=" + JSON.stringify(value) + "; " + new Date('2020-01-01').toGMTString(); },
			del: function(key) { document.cookie = key + "=; " + new Date('2000-01-01').toGMTString(); }
		};
	}

	/*
	 * Cookies disabled, fall back to session storage
	 */
	if(!client.storage) {
		if(debug) console.log('No persistent storage option found, falling back to session storage.');
		
		client.storage = {
			data: {},
			get: function(key) { if(client.storage.data[key]) return JSON.parse(client.storage.data[key]); },
			set: function(key, value) { client.storage.data[key] = JSON.stringify(value); },
			del: function(key) { delete client.storage.data[key]; }
		};
	}

	/*
	 * Poor mans promises, trying to emulate part of node.js q lib
	 */
	var q = {
		defer: function(defer) {
				defer = {
					status: null,
					data: null,
					resolve: function(data) { 
						if(defer.then) {
							defer.then(data); 
							defer.status = true;
						} else {
							defer.data = data;
						}
					},
					reject: function(data) { 
						if(defer.error) {
							defer.error(data);
							defer.status = false;
						} else {
							defer.data = data;
						}
					},
					promise: {
						then: function(callback) {
							if(defer.data && defer.status === true) {
								callback(defer.data);
							} else {
								defer.then = callback; 
								return defer.promise;
							}
						},
						error: function(callback) { 
							if(defer.data && defer.status === false) {
								callback(defer.data);
							} else {
								defer.error = callback;
								return defer.promise;
							}
						}
					},
					then: null,
					error: null
				}
				return defer;
		}
	};

	/*
	 * xhr request from quirksmode.org
	 */
	var request = function(apiMethod, data, path) {
		var defer = q.defer();

		var req = createXMLHTTPObject();
		if(!req) {
			if(debug) console.log('Could not create xhr object!');
			throw new Error('Could not create xhr object!');
		}

		var method = (data) ? 'POST' : 'GET';
		var uri = path ? path : client.apiEndpoint + '/' + client.apiVersion + '/' + apiMethod;

		if(debug) console.log('Method: ' + method + ' uri: ' + uri);

		req.open(method, uri, true);	
		
		req.setRequestHeader('X-LIBVERSION', client.versionString);
		
		if(client.user.session) {
			req.setRequestHeader('X-SESSION', client.user.session);
		}

		if(data) {
			data = JSON.stringify(data);
		}

		req.onreadystatechange = function() {
			if(req.readyState != 4) return;

			if(req.status != 200) {
				defer.reject('status_not_ok');

			} else if(req.getResponseHeader('Content-Type') === 'application/json') { 

				var parsed = null, error = false;
				
				try {
					parsed = JSON.parse(req.responseText);
				} catch(e) {
					error = true;
				}

				if(!error) {
					if(parsed.status == 'ok') {
						if(parsed.payload) defer.resolve(parsed.payload);
						else defer.resolve(parsed.method);
						delete req;
					} else {
						if(parsed.payload) defer.reject(parsed.payload);
						else {
							if(parsed.message) defer.reject(parsed.message);
							else defer.resolve(parsed.method);
						}
						delete req;
					}
				} else {
					if(debug) console.log('Error while parsing JSON, ', req.responseText, defer);
					defer.reject('json_parsing_failed');

					delete req;
				}

			} else if(req.getResponseHeader('Content-Type') === 'text/plain') {  // Used for checking if proxy is alive

				if(req.responseText === 'Ok') {
					delete req.reponseText;
					defer.resolve();
				} else {
					defer.reject();
				}

				delete req;

			} else { // No known usage
				defer.resolve(req.responseText);

				delete req;
			}
		}
		if(req.readyState == 4) {
			defer.reject('status_changed_too_early');

			delete req;
		}

		req.send(data);

		return defer.promise;
	}

	var XMLHttpFactory = null;

	var createXMLHTTPObject = function() {
		var xmlhttp = false;
		var XMLHttpFactories = [
			function () {return new XMLHttpRequest()},
			function () {return new ActiveXObject("Msxml2.XMLHTTP")},
			function () {return new ActiveXObject("Microsoft.XMLHTTP")},
			function () {return new ActiveXObject("Msxml3.XMLHTTP")}
		];

		if(XMLHttpFactory !== null) return  XMLHttpFactories[XMLHttpFactory]();

		for (var i=0; i<XMLHttpFactories.length;i++) {
			try {
				xmlhttp = XMLHttpFactories[i]();
				XMLHttpFactory = i;
			} catch(e) {
				continue;
			}
		}

		return xmlhttp;
	}

	/*
	 * Load session stuff and start initializing everything else if session is found and valid
	 */
	client.init = function() {
		var session = null;

		/*
		 * Check for external login session
		 */
		if(window.location.href.indexOf('ext-login-session') != -1) {
			var queryParams = [];
			window.location.href.slice(window.location.href.indexOf('?') + 1).split('&').forEach(function(hash) {
				hash = hash.split('=');
				queryParams[hash[0]] = hash[1]; 
			});

			session = queryParams['ext-login-session'];
			client.storage.set('session', session);

			/*
			 * Cleanup the extrenal login session from address bar so people dont bookmark it..
			 */
			if(window.history.pushState) {
				window.history.pushState(null, document.title, window.location.href.split('?')[0]);	
			}
		} else {
			session = client.storage.get('session');
		}
		
		if(!session) {
			client.emit('loginRequired');
			return;
		}

		client.user.session = session;

		client.user.checkSession()
			.then(function() {
				getSettings();
				setTimeout(keepalive, 1000 * 60);
			})
			.error(function() {
				delete client.user.session;
				client.storage.del('session');
				client.emit('loginRequired');
			});
	}


	/*
	 * Event emitter type of thing
	 */
	var listeners = {};
	client.on = function(event, callback) {
		if(!listeners[event]) listeners[event] = [];

		listeners[event].push(callback);
	}

	client.emit = function(event, data) {
		if(debug) console.log(event);
		if(!listeners[event]) return;
		for(var i=0; i<listeners[event].length; i++) {
			listeners[event][i](data);
		}
	}

	/*
	 * Api - User handler
	 */
	client.documentation.user = {
		logout:       { 'parameters': null, 'return': { 'success': 'logout_ok', 'fail': 'error_in_logout' } },
		checkSession: { 'parameters': null, 'return': { 'success': 'Session object', 'fail': 'unknown_error, no_session_found' } },
		info:         { 'parameters': null, 'return': { 'success': 'User object', 'fail': 'unknown_error, no_session_found, no_user_found' } },
		listSessions: { 'parameters': null, 'return': { 'success': '[Session objects]', 'fail': 'unknown_error, no_session_found, no_user_found, no_sessions' } },
		settings:     { 'parameters': null, 'return': { 'success': '[Settings objects]', 'fail': 'unknown_error, no_session_found, no_user_found' } },
		login:        { 'parameters': {'email': 'Email address', 'password': 'Password'}, 'return': { 'success': 'Session object', 'fail': 'unknown_error, not_found, invalid_password, email_not_verified, failed_to_start_session'} },
		register:     { 'parameters': {'email': 'Email address', 'password': 'Password'}, 'return': { 'success': 'User object', 'fail': 'failed, email_in_use, invalid_email, password_too_short, salt_error, hash_error, failed_insert_user' } },
		setSetting:   { 'parameters': {'key': 'value'}, 'return': { 'success': 'setting_saved', 'fail': 'unknown_error, no_session_found, no_user_found' } },
		edit:         { 'parameters': {'data': 'object with key->value pair of all user data (ie. email, password)' }, 'return': { 'success': 'pipe', 'fail': 'pipe' } }
	};

	Array('checkSession', 'info', 'listSessions', 'settings').forEach(function(method) {
		client.user[method] = function() {
			return request('user/'+method);
		};
	});

	client.user.logout = function() {
		var defer = q.defer();
		request('user/logout')
			.then(function(status) {
				defer.resolve(status);
				client.emit('loginRequired');
			})
			.error(function(message) {
				defer.reject(message);
			})
		return defer.promise;
	}

	client.user.login = function(email, password) {
		var defer = q.defer();
		request('user/login', {email: email, password: password})
			.then(function(session) {
				if(debug) console.log('Started new session ' + session)
				client.user.session = session;
				client.storage.set('session', session);
				defer.resolve(session);
				getSettings();
				setTimeout(keepalive, 1000 * 60);
			})
			.error(function(message) {
				if(debug) console.log('Request failed with message: ' + message);
				defer.reject(message);
			});
		return defer.promise;
	}

	client.user.externalLogin = function(service) {
		if(!['facebook','twitter','paypal'].indexOf(service) == -1) throw new Error('Service ' + service + ' not supported as external login service!');
		window.location.href = client.loginService + '/' + service + '?return_url=' + window.location.href.split('?')[0];
	}

	client.user.register = function(email, password) {
		return request('user/register', {email: email, password: password, return_url: window.location.href.split('?')[0]});
	}

	client.user.setSetting = function(key, value) {
		return request('user/setSetting', {key: key, value: value});
	}

	client.user.edit = function(data) {
		return request('user/edit', {data: data});
	}

	function getSettings() {
		client.user.settings()
			.then(function(settings) {
				client.settings = {};
				settings.forEach(function(setting) {
					client.settings[setting.setting] = setting.value;
				});
				getCacheServers();
			})
			.error(function() {
				getCacheServers();
			});	
	}

	function keepalive() {
		client.user.checkSession()
			.then(function() {
				setTimeout(keepalive, 1000 * 60);		
			})
			.error(function() {
				client.emit('sessionTimeout');
				delete client.user.session;
				client.emit('loginRequired');
			});
			
		var testFile = 'https://' + client.cacheServers[0].host + '/check.jpg?'+new Date().getTime();

		var _tmp = new Image();

		_tmp.onload = function() {
			// all ok
		}
		_tmp.onerror = function() {
			if(debug) console.log('Cache server check fail!');
			client.cacheServers.splice(0,1);
		}
		_tmp.src = testFile;
	}

	/*
	 * Api - streams
	 */
	client.documentation.streams = {
		get: { 'parameters': null, 'return': null }
	};

	client.streams.get = function() {
		var defer = q.defer();

		request('streams/get')
			.then(function(streams) {
				var out = [];
				streams.forEach(function(stream) {
					var outStream = {
						name: stream.name,
						visibleName: stream.visibleName,
						hls: {
							path: '/live/' + stream.name + '.m3u8',
							levels: []
						},
						path: '/live/' + stream.name + '.ts',
						screenshots: []
					};
					
					stream.hlsLevels.forEach(function(level) {
						level.path = '/live/remux/' + stream.name + '_' + level.name + '.m3u8'
						outStream.hls.levels.push(level);
					});

					Object.keys(stream.screenshots).forEach(function(key) {
						outStream.screenshots.push({
							jpg: '/live/' + stream.name + '_' + key + '.jpg',
							mjpg: '/live/' + stream.name + '_' + key + '.mjpg',
							width: stream.screenshots[key].width,
							height: stream.screenshots[key].height
						});
					});

					out[stream.streamOrder-1] = outStream;
				});

				defer.resolve(out);
			})
			.error(function(err) {
				if(debug) console.log(err);
			});

		return defer.promise;
	}

	/*
	 * Api - epg
	 */
	client.documentation.epg = {
		current: { 'parameters': {'streams': 'Array of stream names to get epg for (optional)'}, 'return': { 'success': 'EPG data', 'fail': 'error_in_query' } },
		next:    { 'parameters': {'streams': 'Array of stream names to get epg for (optional)'}, 'return': { 'success': 'EPG data', 'fail': 'error_in_query' } },
		range:   { 'parameters': {'from': 'Time from', 'to': 'Time to', 'streams': 'Array of stream names to get epg for (optional)'}, 'return': { 'success': 'EPG data', 'fail': 'error_in_query' } },
		info: { 'parameters': {'pid': 'single pid or array of pids'}, 'return': { 'success': 'EPG entry or array with epg entries', 'fail': 'pid_not_found' } },
		search: { 'parameters': { 'string': 'String to search for'}, 'return': { 'success': 'EPG data', fail: 'search_error'} }
	};

	client.epg.current = function(streams) {
		return request('epg/current', {streams: streams});
	}

	client.epg.next = function(streams) {
		return request('epg/next', {streams: streams});
	}

	client.epg.range = function(from, to, streams) {
		return request('epg/range', {from: new Date(from).toISOString(), to: new Date(to).toISOString(), streams: streams});
	}

	client.epg.info = function(pid) {
		return request('epg/info', {pid: pid});
	}

	client.epg.titles = function() {
		return request('epg/titles');
	}

	client.epg.search = function(string) {
		return request('epg/search', {search: string});
	}

	client.epg.titleSearch = function(title) {
		return request('epg/titleSearch', {search: title})
	}

	/*
	 * Api - vod
	 */
	client.documentation.vod = {
		info: { 'parameters': {'pid': 'Get VOD information about single program by PID'}, 'return': { 'success': 'VOD information', 'fail': null } },
		getUrl: { 'parameters': {'pid': 'PID of VOD object', 'path': 'Path of VOD object', 'file': 'File to request'}, 'return': 'Full url to file' },
		getPlaylist: { 'parameters': {'vodObject': 'Vod object', 'qualities': 'Array of qualities to get playlist in.'}, 'return': 'Url to playlist'},
		getDownload: { 'parameters': {'vodObject': 'Vod object', 'format': 'Format to download in, possible values: mp4, ts' ,'quality': 'Quality of download'}, 'return': 'Url to download'}
	};

	client.vod.info = function(pid) {
		return request('vod/info', {pid: pid});
	}

	client.vod.getPlaylist = function(vodObject, qualities) {
		var quality = '';
		if(qualities && Object.prototype.toString.call(qualities) === '[object Array]') {
			quality = '?levels=' + qualities.join(',');
		}
		return client.cache.getUrl('/vod' + vodObject.recordpath + 'master.m3u8' + quality)
	}

	client.vod.getDownload = function(vodObject, format, quality) {
		if(!vodObject.downloadFormats && !vodObject.downloads) throw new Error('Not available for download');
		if(!vodObject || !quality) throw new Error('Invalid parameters');
		if((vodObject.downloadFormats && vodObject.downloadFormats[format].indexOf(quality) != -1) || vodObject.downloads) {
			var start = new Date.fromISO(vodObject.start);
			var date = (''+start.getFullYear()).substr(2,2) + ( ( start.getMonth() + 1 < 10 ) ? '0' + ( start.getMonth() + 1 ) : ( start.getMonth() + 1 ) ) + ( ( start.getDate() < 10 ) ? '0' + start.getDate() : start.getDate() );
			var time = ( ( start.getHours() < 10 ) ? '0' + start.getHours() : start.getHours() ) + '' + ( ( start.getMinutes() < 10 ) ? '0' + start.getMinutes() : start.getMinutes() );
			var fileTitle = vodObject.title.fi.replace(/ \(([0-9]+)\)/,'').replace(/[áàâäå]/g, 'a').replace(/[óòôö]/g,'o').replace(/[ÁÂÄÅ]/g,'A').replace(/[ÒÓÔÖ]/g,'O').replace(/[^A-Za-z0-9\-_]/g, '-');
			fileTitle = fileTitle.replace(/ \([a-zA-Z0-9]+\)/g,'');
			fileTitle = fileTitle.replace(/[^\w|^ä|^ö|^ü|^Ä|^Ö|^Ü|^ß]/g, "_" );

			// title - date - time - quality - channel
			var fileName = fileTitle + '-' + date + '-' + time + '-' + quality + '-' + vodObject.channel;
			return client.cache.getUrl('/vod' + vodObject.recordpath + quality + '/' + fileName + '.' + format);
		}
		else throw new Error('Quality / format not found');
	}

	client.vod.getUrl = function(path, file) {
		return client.cache.getUrl('/vod' + path + file);
	}

	/*
	 * Api - cache (private, autorun on user login)
	 */

	function getCacheServers(refresh) {
		request('cache/get')
			.then(function(servers) {
				client.cache.servers = servers;
				var speedtestAmount = servers.length, speedtestDone = 0, speedtests = {};

				/*
				 * Merge speedtests already done
				 */
				if(!refresh && client.settings.speedtests && servers.length == Object.keys(client.settings.speedtests).length && (client.settings && client.settings.speedtests && typeof client.settings.speedtests == 'object' && Object.keys(client.settings.speedtests).length > 0)) {
					speedtests = client.settings.speedtests;
					servers.forEach(function(server) {
						if(client.settings.speedtests[server.host]) {
							server.speedtest = client.settings.speedtests[server.host];
							speedtestAmount--;
						}
					});
				}

				var testedServers = [];

				/*
				 * Run speedtest for each server that doesn't have speedtest run to it yet
				 */
				function speedtestRun() {
					var server = servers.pop();
					if(!server) {
						testedServers.sort(function(server1, server2) {
							return (server1.speedtest.mbit > server2.speedtest.mbit)?-1:1;
						});

						if(testedServers.length > 2) {
							// If speedtest between top 2 servers are withing 40% of eachother and 2nd server is over 6mbit, see which one has lowest latency
							var diff = (testedServers[0].speedtest.mbit / testedServers[1].speedtest.mbit);
							if(testedServers[0].speedtest.latency > testedServers[1].speedtest.latency && (diff > 0.6 || diff < 1.6) && testedServers[1].speedtest.mbit > 6) {
								var _tmp = testedServers[0];
								testedServers[0] = testedServers[1];
								testedServers[1] = _tmp;
							}
						}

						client.cacheServers = testedServers;

						client.emit('speedtestDone', testedServers);

						if(client.settings && client.settings.speedtests) client.settings.speedtests = speedtests;

						if(speedtestAmount == 0) {
							client.emit('ready');
							return;
						}

						client.user.setSetting('speedtests', speedtests)
								.then(function() {
									client.emit('ready');
								})
								.error(function() {
									if(debug) console.log('Setting setting failed!');
									client.emit('error', 'Error while saving settings');
								});
						return;
					}
					
					if(server.speedtest) {
						testedServers.push(server);
						speedtestRun();
						return;
					}

					client.cache.speedtest(server)
						.then(function(data) {
							server.speedtest = data;
							speedtests[server.host] = data;
							testedServers.push(server);
							speedtestDone++;
							client.emit('speedtestProgress',{total: speedtestAmount, done: speedtestDone, server: server});
							speedtestRun();
						})
						.error(function(err) {
							if(debug) console.log('Error while speedtesting: ' + err);
							speedtestDone++;
							client.emit('speedtestProgress',{total: speedtestAmount, done: speedtestDone});
							speedtestRun();
						});
				}


				client.emit('speedtestStart',{total: speedtestAmount, done: 0, servers: servers});
				speedtestRun();
			})
			.error(function(message) {
				if(debug) console.log(message);
			});
	}

	/*
	 * Speedtest cache servers
	 */
	client.documentation.cache = {
		runSpeedtests: { 'parameters': 'none', 'return': 'none' },
		speedtest: { 'parameters': {'server': 'Cache server object'}, 'return': 'Promise with test result' },
		getUrl: { 'parameters': {'path': 'Path to generate full url for', 'cacheServer': 'Override default cache server selection' }, 'return': 'Full url for path' }
	};

	client.cache.runSpeedtests = function() {
		getCacheServers(true);
	}

	client.cache.speedtest = function(server) {
		var defer = q.defer();
		var startTime = new Date().getTime();
		var latencyFile = 'https://' + server.host + '/check.jpg?' + new Date().getTime();
		var testFile = 'https://' + server.host + '/speedtest.jpg?' + new Date().getTime();
		var bytes = 719431;

		var _tmp = new Image();
	
		_tmp.onload = function() {
			var duration = new Date().getTime() - startTime;
			var latencyStart = new Date().getTime();

			var _tmp = new Image();
			
			_tmp.onload = function() {
				defer.resolve({
					mbit: (((bytes/1024)/1024)*8)/(duration/1000),
					length: duration/1000,
					latency: (new Date().getTime() - latencyStart)
				});
			}

			_tmp.onerror = function() {
				defer.resolve({
					mbit: (((bytes/1024)/1024)*8)/(duration/1000),
					length: duration/1000,
					latency: -1
				});
			}

			_tmp.src = latencyFile;
		}
		_tmp.onerror = function() {
			defer.resolve({
				mbit: 0,
				length: 0,
				latency: -1
			});
		}
		_tmp.src = testFile;
		return defer.promise;
	}


	client.cache.getUrl = function(path, cacheServer) {
		var url = 'https://' + (cacheServer?cacheServer:client.cacheServers[0].host) + '/' + client.user.session + path
		return url;
	}

	/*
	 * News
	 */
	client.documentation.news = {
		get: { 'parameters': 'none', 'return': 'Array of news objects' },
		add: { 'parameters': {'title': 'Title of news', 'author': 'Name of author', 'content': 'Content of news'}, 'return': 'News object' }
	};

	client.news.get = function() {
		return request('news/get');
	}

	client.news.add = function(title, author, content) {
		return request('news/add', {title: title, author: author, content: content});
	}

	/*
	 * Time
	 */
	client.documentation.time = {
		get: { 'parameters': 'none', 'return': 'ISO String of current server time' }
	};

	client.time.get = function() {
		return request('time/get');
	}


	/*
	 * Api - Api info
	 */
	client.__info__ = function() {
		var defer = q.defer();
		request('api/__info__')
			.then(function(apiInfo) {
				var info = {
					client: {
						version: client.versionString,
						apiVersion: client.apiVersion,
						apiEndpoint: client.apiEndpoint,
						modules: client.documentation
					},
					api: apiInfo
				};
				defer.resolve(info);
			});

		return defer.promise;
	}

	return client;
};

// Polyfill for IE8/IE9 support
if(!Array.prototype.forEach){Array.prototype.forEach=function(a,b){var T,k;if(this==null){throw new TypeError(' this is null or not defined');}var O=Object(this);var c=O.length>>>0;if(typeof a!=="function"){throw new TypeError(a+' is not a function');}if(arguments.length>1){T=b}k=0;while(k<c){var d;if(k in O){d=O[k];a.call(T,d,k,O)}k++}}}if(!window.JSON){window.JSON={parse:function(a){return eval('('+a+')')},stringify:(function(){var toString=Object.prototype.toString;var d=Array.isArray||function(a){return toString.call(a)==='[object Array]'};var e={'"':'\\"','\\':'\\\\','\b':'\\b','\f':'\\f','\n':'\\n','\r':'\\r','\t':'\\t'};var f=function(m){return e[m]||'\\u'+(m.charCodeAt(0)+0x10000).toString(16).substr(1)};var g=/[\\"\u0000-\u001F\u2028\u2029]/g;return function stringify(a){if(a==null){return'null'}else if(typeof a==='number'){return isFinite(a)?a.toString():'null'}else if(typeof a==='boolean'){return a.toString()}else if(typeof a==='object'){if(typeof a.toJSON==='function'){return stringify(a.toJSON())}else if(d(a)){var b='[';for(var i=0;i<a.length;i++)b+=(i?', ':'')+stringify(a[i]);return b+']'}else if(toString.call(a)==='[object Object]'){var c=[];for(var k in a){if(a.hasOwnProperty(k))c.push(stringify(k)+': '+stringify(a[k]))}return'{'+c.join(', ')+'}'}}return'"'+a.toString().replace(g,f)+'"'}})()}}if(!Object.keys){Object.keys=(function(){'use strict';var hasOwnProperty=Object.prototype.hasOwnProperty,hasDontEnumBug=!({toString:null}).propertyIsEnumerable('toString'),dontEnums=['toString','toLocaleString','valueOf','hasOwnProperty','isPrototypeOf','propertyIsEnumerable','constructor'],dontEnumsLength=dontEnums.length;return function(a){if(typeof a!=='object'&&(typeof a!=='function'||a===null)){throw new TypeError('Object.keys called on non-object');}var b=[],prop,i;for(prop in a){if(hasOwnProperty.call(a,prop)){b.push(prop)}}if(hasDontEnumBug){for(i=0;i<dontEnumsLength;i++){if(hasOwnProperty.call(a,dontEnums[i])){b.push(dontEnums[i])}}}return b}}())}(function(){var D=new Date('2011-06-02T09:34:29+02:00');if(!D||+D!==1307000069000){Date.fromISO=function(s){var a,tz,rx=/^(\d{4}\-\d\d\-\d\d([tT ][\d:\.]*)?)([zZ]|([+\-])(\d\d):(\d\d))?$/,p=rx.exec(s)||[];if(p[1]){a=p[1].split(/\D/);for(var i=0,L=a.length;i<L;i++){a[i]=parseInt(a[i],10)||0};a[1]-=1;a=new Date(Date.UTC.apply(Date,a));if(!a.getDate())return NaN;if(p[5]){tz=(parseInt(p[5],10)*60);if(p[6])tz+=parseInt(p[6],10);if(p[4]=='+')tz*=-1;if(tz)a.setUTCMinutes(a.getUTCMinutes()+tz)}return a}return NaN}}else{Date.fromISO=function(s){return new Date(s)}}})();if(!Array.prototype.indexOf){Array.prototype.indexOf=function(a,b){var k;if(this==null){throw new TypeError('"this" is null or not defined');}var O=Object(this);var c=O.length>>>0;if(c===0){return-1}var n=+b||0;if(Math.abs(n)===Infinity){n=0}if(n>=c){return-1}k=Math.max(n>=0?n:c-Math.abs(n),0);while(k<c){if(k in O&&O[k]===a){return k}k++}return-1}}if(!Date.prototype.toISOString){(function(){function pad(a){if(a<10){return'0'+a}return a}Date.prototype.toISOString=function(){return this.getUTCFullYear()+'-'+pad(this.getUTCMonth()+1)+'-'+pad(this.getUTCDate())+'T'+pad(this.getUTCHours())+':'+pad(this.getUTCMinutes())+':'+pad(this.getUTCSeconds())+'.'+(this.getUTCMilliseconds()/1000).toFixed(3).slice(2,5)+'Z'}}())}
