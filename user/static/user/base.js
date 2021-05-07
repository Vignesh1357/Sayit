function openNav() {
    document.getElementById("mySidenav").style.width = "200px";
  }

  function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
  }

var s3 = new AWS.S3({
    signatureVersion: 'v4'
    });