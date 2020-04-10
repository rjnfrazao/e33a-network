var global_posts: [];

document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document.querySelector("#post-form-submit").addEventListener("click", post); // event to open inbox mailbox

  //  document
  //    .querySelector("#sent")
  //    .addEventListener("click", () => load_mailbox("sent")); // event to open the sent mailbox

  // By default, load all posts
  allpost();
});

//
//
//
function allpost() {
  // Hide the error message
  document.querySelector("#error-message").innerHTML = "";
  document.querySelector("#error-message").style.display = "none";

  // Hide all other pages
  document.querySelector("#allposts").style.display = "block";
  document.querySelector("#profile").style.display = "none";

  // load the post messages
  load_posts();
}

function post() {
  fetch("/post", {
    method: "POST",
    body: JSON.stringify({
      message: document.querySelector("#message").value,
    }),
  }).then(function (response) {
    console.log("recebeu resposta do post");
    if (response.status >= 200 && response.status < 300) {
      // Post message successfully
      // hide div with used to display error message
      document.querySelector("#error-message").innerHTML = "";
      document.querySelector("#error-message").style.display = "none";
      load_posts(); // PAREI AQUI IMPLEMENTANDO O LOAD DO POST QUE SERIA CARREGADO NO REACT.
    } else {
      // Error was returned. Extract error content.
      response.json().then(function (data) {
        // Display error message.
        document.querySelector("#error-message").innerHTML = data.error;
        document.querySelector("#error-message").style.display = "block";
        window.scrollTo(0, 0);
        return false;
      });
    }
  });
  event.preventDefault();
}

function load_posts() {
  fetch("/get_posts", {
    method: "GET",
  })
    .then(function (response) {
      if (response.status >= 200 && response.status < 300) {
        // Post message successfully
        // hide div with used to display error message
        document.querySelector("#error-message").innerHTML = "";
        document.querySelector("#error-message").style.display = "none";
        return response.json();
      } else {
        // Error was returned. Extract error content.
        response.json().then(function (data) {
          // Display error message.
          document.querySelector("#error-message").innerHTML = data.error;
          document.querySelector("#error-message").style.display = "block";
          window.scrollTo(0, 0);
          return false;
        });
      }
    })
    .then((posts) => {
      global_posts = [...posts];
      console.log("Fetch =>", posts); // PAREI AQUI, NÃO CONSIGO PEGAR O CONTEUDO E O REACT OBJECT ESTÁ ERRADO
      return posts;
    });
}
