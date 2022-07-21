const next = document.getElementById("next_btn");
const prev = document.getElementById("prev_btn");
const save = document.getElementById("save_btn");
const undo = document.getElementById("undo_btn");
const clear = document.getElementById("clear_btn");
const label_text_box = document.getElementById("label");
const add_option = document.getElementById("add_option");
const remove_option = document.getElementById("remove_option");
const option_text_box = document.getElementById("option_text_box");
// canvas that shows image
const canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");
// canvas used to draw
const overlay = document.getElementById("overlay");
let ctxo = overlay.getContext("2d");
// canvas used to show rects
const rects = document.getElementById("rects");
let ctxr = rects.getContext("2d");

function draw(rect, canvasContext, label="None", lineWidth="3", strokeColor="red") {
  if(label != "None") {
    canvasContext.font = "16px Arial";
    canvasContext.fillStyle = strokeColor;
    canvasContext.fillText(label, rect[0]+1, rect[1]+16)
  }
  canvasContext.lineWidth = lineWidth;
  canvasContext.strokeStyle = strokeColor;
  canvasContext.strokeRect(...rect);
}

let rectangles = [];

var offsetX;
var offsetY;

var startX, startY;
var isDown = false;

var prevStartX = 0;
var prevStartY = 0;
var prevWidth = 0;
var prevHeight = 0;


overlay.addEventListener('mousedown', (e) => {
  e.preventDefault();
  e.stopPropagation();
  startX = parseInt(e.clientX - (offsetX - window.scrollX));
  startY = parseInt(e.clientY - (offsetY - window.scrollY));
  isDown = true;
});

overlay.addEventListener('mousemove', (e) => {
  e.preventDefault();
  e.stopPropagation();
  if(!isDown) {
    return;
  }
  mouseX = parseInt(e.clientX - (offsetX - window.scrollX));
  mouseY = parseInt(e.clientY - (offsetY - window.scrollY));
  var width = mouseX - startX;
  var height = mouseY - startY;
  ctxo.clearRect(0, 0, canvas.width, canvas.height);
  draw([startX, startY, width, height], ctxo);
  prevStartX = startX;
  prevStartY = startY;
  prevWidth = width;
  prevHeight = height;
});

overlay.addEventListener('mouseup', (e) => {
  e.preventDefault();
  e.stopPropagation();
  const label = label_text_box.value;
  const r = [prevStartX, prevStartY, prevWidth, prevHeight, label];
  rectangles.push(r);
  draw(r.slice(0, r.length), ctxr, label);
  ctxo.clearRect(0, 0, canvas.width, canvas.height);
  isDown = false;
});

overlay.addEventListener('mouseout', (e) => {
  e.preventDefault();
  e.stopPropagation();
  isDown = false;
});

function load_img(url) {
  let img = new Image();
  img.src = 'static/'+url;
  img.onload = function() {
    canvas.width = this.width; 
    canvas.height = this.height;
    offsetX = canvas.getBoundingClientRect().left;
    offsetY = canvas.getBoundingClientRect().top;
    overlay.width = this.width;
    overlay.height = this.height;
    rects.width = this.width;
    rects.height = this.height;
    img.style.display = 'none';
    ctx.drawImage(img, 0, 0, this.width, this.height);
  }
};


add_option.addEventListener('click', (e) => {
  e.preventDefault();
  e.stopPropagation();
  var option = document.createElement("option");
  option.text = option_text_box.value;
  label_text_box.add(option);
  option_text_box.value = '';
});

remove_option.addEventListener('click', (e) => {
  e.preventDefault();
  e.stopPropagation();
  if(label_text_box.selectedIndex != 0) { // 0 is None
    label_text_box.remove(label_text_box.selectedIndex);
  }
});

save.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  let data = {rects : rectangles};
  fetch("/save", {
    method: "POST",
    headers: {'Content-Type': 'application/json'}, 
    body: JSON.stringify(data)
  }).then(res => res.json()).catch(err => {
    console.log(err);
  });
  alert("Saved XML!");
});

prev.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  let perm = true;
  if(rectangles.length > 0) {
    perm = confirm("If you are going back, all the boxes you drew will reset!");
  }
  if(perm) {
    rectangles = [];
    fetch("/prev", {
      method: "POST"
    }).then(res => res.json()).then(text => {
      load_img(text.filename);
    }).catch(err => {
      console.log(err);
    });
  }
});
next.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  let perm = true;
  if(rectangles.length > 0) {
    perm = confirm("If you are going to the next image, all the boxes you drew will reset!");
  }
  if(perm) {
    rectangles = [];
    fetch("/next", {
      method: "POST"
    }).then(res => res.json()).then(text => {
      load_img(text.filename);
    }).catch(err => {
      console.log(err);
    });
  }
});
undo.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  ctxr.clearRect(0, 0, rects.width, rects.height);
  rectangles.pop(); 
  for(let i = 0; i < rectangles.length; i++) {
    draw(rectangles[i].slice(0, rectangles[i].length), ctxr, rectangles[i][rectangles[i].length-1])
  }
});

clear.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  let perm = confirm("Clearing will remove all boxes! Are you sure you want to do this?");
  if(perm) {
    ctxr.clearRect(0, 0, rects.width, rects.height);
    ctxo.clearRect(0, 0, overlay.width, overlay.height);
    rectangles = [];
  }
});

fetch("/cur", {
  method: "POST"
}).then(res => res.json()).then(text => {
  load_img(text.filename);
}).catch(err => {
  console.log(err);
});