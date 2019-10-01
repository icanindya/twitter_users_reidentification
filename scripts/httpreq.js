function makeHttpGetRequest(url){
    var response = {};
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, false);
    xhr.send();
    response.status = xhr.status;
    response.response_text = xhr.responseText;
    return response;
}

