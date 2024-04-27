function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/home";
  });
}

function myFunction() {
  var x = document.lastModified;
  var lastModified = new Date(x);
  lastModified.setHours(lastModified.getHours() + 5); // Add 5 hours for IST
  lastModified.setMinutes(lastModified.getMinutes() + 30); // Add 30 minutes for IST
  document.getElementById("demo").innerHTML = lastModified.toISOString().substr(11, 8);


}
myFunction()