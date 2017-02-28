var editRefreshInterval = 5000;
var timerId = setInterval("fireInterval()", editRefreshInterval);
var text = '';
var fireInt = true;

//Setup the server object
var server = {};
InstallFunction(server, 'Add');
InstallFunction(server, 'ConvertMarkdown');

if( !window.XMLHttpRequest ) XMLHttpRequest = function()
{
  try{ return new ActiveXObject("Msxml2.XMLHTTP.6.0") }catch(e){}
  try{ return new ActiveXObject("Msxml2.XMLHTTP.3.0") }catch(e){}
  try{ return new ActiveXObject("Msxml2.XMLHTTP") }catch(e){}
  try{ return new ActiveXObject("Microsoft.XMLHTTP") }catch(e){}
  throw new Error("Could not find an XMLHttpRequest alternative.")
};


function Request(function_name, opt_argv) {

	  if (!opt_argv)
	    opt_argv = new Array();
	 
	  // Find if the last arg is a callback function; save it
	  var callback = null;
	  var len = opt_argv.length;
	  if (len > 0 && typeof opt_argv[len-1] == 'function') {
	    callback = opt_argv[len-1];
	    opt_argv.length--;
	  }
	  var async = (callback != null);
	 
	  // Build an Array of parameters, w/ function_name being the first parameter
	  var params = new Array(function_name);
	  for (var i = 0; i < opt_argv.length; i++) {
	    params.push(opt_argv[i]);
	  }
	  var body = JSON.stringify(params);

	  // Create an XMLHttpRequest 'POST' request w/ an optional callback handler 
	  var req = new XMLHttpRequest();
	  req.open('POST', '/rpc', async);
	 
	  req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	  req.setRequestHeader("Content-length", body.length);
	  req.setRequestHeader("Connection", "close");

	  if (async) {
	    req.onreadystatechange = function() {
	      if(req.readyState == 4 && req.status == 200) {
	        var response = null;
	        try {
	         response = JSON.parse(req.responseText);
	        } catch (e) {
	         response = req.responseText;
	        }
	        callback(response);
	      }
	    }
	  }
	 
	  // Make the actual request
	  req.send(body);
}

function InstallFunction(obj, name) {
	obj[name] = function() { Request(name, arguments); }
}

function fireInterval() {
    //so we don't get multiple intervals during the same period
    newText = window.document.getElementById('textarea').value;
    if (newText != text) {
    	try {
    		processChangedText();
    	} catch (err) {
    		alert('An error occured: ' + err);
    	}
        text = newText;
    }
}

function processChangedText() {
    //var editArea = window.document.getElementById('editarea');
    var editTextArea = window.document.getElementById('textarea');
    server.ConvertMarkdown(editTextArea.value, convertMarkdownCallback);
}

function convertMarkdownCallback(response) {
	var editArea = window.document.getElementById('editarea');
	var title = window.document.getElementById('titleInput');
	var innerHtml = '<h1>' + title.value + '</h1>' + response;
	editArea.innerHTML = innerHtml;
}
function addCallback(response) {
	alert(response);
}


