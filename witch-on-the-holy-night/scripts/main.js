//图片组件的循环切换功能
let myImage = document.querySelector("img");
let img = [1, 2, 3, 4, 5,];
var n = 1;
myImage.onclick = function () {
  myImage.setAttribute("src", "images/" + img[n++] + ".jpg");
  if (n > img.length - 1) {
    n = 0; 
  }
};


//切换用户名（储存在浏览器中）
let myButton = document.querySelector("button");
let myHeading = document.querySelector("h1");

function setUserName() {
  let myName = prompt("请输入你的名字。");
  if (!myName) {
    setUserName();
  } else {
    localStorage.setItem("name", myName);
    myHeading.textContent = "Welcome，" + myName + "!";
  }
}
if (!localStorage.getItem("name")) {
  setUserName();
} else {
  let storedName = localStorage.getItem("name");
  myHeading.textContent = "Welcome，" + storedName + "!";
}
myButton.onclick = function () {
  setUserName();
};
