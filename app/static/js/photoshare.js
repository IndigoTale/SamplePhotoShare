function clickHeartButton(photo_id){
    var request = new XMLHttpRequest();
    var url = "/heart";
    var data = '{"photo_id":"'+photo_id+'"}';
    request.open('POST',url);
    request.setRequestHeader('content-type','application/json');
	request.send(data);
	request.onreadystatechange = function() {
		if (request.readyState === 4 && request.status === 200){  
            var res = JSON.parse(request.responseText);

            if(res.push == true){
                var photoFrame = document.getElementById(photo_id);
                console.log(photoFrame);
            }
        }   
    }
}

