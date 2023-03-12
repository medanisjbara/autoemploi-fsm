/*
    Frontend runtime scripts for Autodevoir@FSM
    Author : Zaafouri Mohamed Rayen
    E-mail : mohamedrayenzaafouri@gmail.com
*/

//Post-loading events.
window.addEventListener("load", (event) => {
    if(document.getElementsByTagName("rayenui")[0]!=null){
    //Loading previous search items after DOM rendering.
    let current_search_history = JSON.parse(localStorage.getItem("request_history"));
    for(i=0;i<current_search_history.length;i++){
        let li = document.createElement("li");
        let span = document.createElement("span");
        span.textContent = current_search_history[i];
        let button = document.createElement("button");
        button.addEventListener("click",(event) => {
            event.stopPropagation();
            removeHistoryItem(button.parentElement.firstElementChild.innerHTML);
            button.parentElement.remove();
            
        });
        li.append(span,button);
        li.addEventListener("click",(event)=>{
            document.getElementsByTagName("form")[0].firstElementChild.value = span.textContent;
            document.getElementsByTagName("form")[0].requestSubmit();
        });
        document.getElementsByClassName("previously")[0].append(li);
    }
    //Search form submission event interception to cache the search query.
    let search_form = document.getElementsByTagName("form")[0];
    search_form.addEventListener("submit",(event) =>{

        event.preventDefault();
        addHistoryItem(document.getElementsByClassName("input-text")[0].value);
        search_form.submit();
    });
    }
});




//Initializing browser's local storage for proper use.
let request_history = localStorage.getItem("request_history");
if(request_history==null){
    localStorage.setItem("request_history",JSON.stringify([]));
}


//Browser local storage misc functions.
function removeHistoryItem(item){
    let aux = JSON.parse(localStorage.getItem("request_history"));
    var arr = [];
    for(i=0;i<aux.length;i++){
        if(aux[i]==item){
            continue;
        }
        arr.push(aux[i]);
    }
    localStorage.setItem("request_history",JSON.stringify(arr));

}

function addHistoryItem(item){
    let aux = JSON.parse(localStorage.getItem("request_history"));
   if(aux!=null){
    if(aux.length==0){
        aux.push(item);
    }
    else{
        for(i=0;i<aux.length;i++){
            if(aux[i]===item){
                return;
            }
        }
        aux.push(item);
    }
}
 
    localStorage.setItem("request_history",JSON.stringify(aux));
}

//Picture full screen feature.

function display_image_fs(url){
    let image_container = document.createElement("div");
    image_container.setAttribute("class","fs-image-preview");
    let image = document.createElement("img");
    image.setAttribute("src",url);
    image.addEventListener("click",(event)=>{
        //preventing the image click event to reach its container and fire the closing event
        event.stopPropagation();
    })
    image_container.appendChild(image);    
    document.body.appendChild(image_container);

    image_container.addEventListener("click",(event)=>{
        image_container.remove();
    }
        );
}

document.addEventListener("load", (event)=>{
    let image_elements = document.getElementsByClassName("result-img");
    for (let i=0;i<image_elements.length;i++){
        image_elements[i].addEventListener("click",(event)=>{
                display_image_fs(image_elements[i].getAttribute("src"));
        });
    }
});



console.log("Frontend modules should perform as intended.");