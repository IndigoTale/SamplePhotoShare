function clickHeartButton(photo_id){
    var request = new XMLHttpRequest();
    var url = "https://photoshare.tk/heart";
    var data = '{"photo_id":"'+photo_id+'"}';
    request.open('POST',url);
    request.setRequestHeader('content-type','application/json');
	request.send(data);
	request.onreadystatechange = function() {
		if (request.readyState === 4 && request.status === 200){  
            var res = JSON.parse(request.responseText);

            if(res.push == true){
                var photoFrame = document.getElementById(photo_id);
                var count = photoFrame.textContent;
                count = parseInt(count) + 1;
                photoFrame.innerHTML = '<img src="https://photoshare.tk/static/img/icon-heart-pink.png">'+String(count);
                console.log(photoFrame);
            }
            else{
                var photoFrame = document.getElementById(photo_id);
                var count = photoFrame.textContent;
                count = parseInt(count) - 1;
                photoFrame.innerHTML = '<img src="https://photoshare.tk/static/img/icon-heart.png">'+String(count);
            }
        }   
    }
}

