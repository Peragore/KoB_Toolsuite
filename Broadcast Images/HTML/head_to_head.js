setInterval(function() {

    let myImageElementHidden = document.getElementById('myImage_hidden');
    myImageElementHidden.src = '../head_to_head.png?rand=' + Math.random();

    if (myImageElementHidden.naturalHeight != 0){
        let myImageElement = document.getElementById('myImage');
        myImageElement.src = '../head_to_head.png?rand=' + Math.random();
    }

}, 2000);