











// function abc() {     // function expression closure to contain variables
//   var i = 0;
//   var pics = [ "assets/refresh.svg" ];
//   var el = document.getElementById('icon');  // el doesn't change
//   function toggle() {
//       el.src = "assets/refresh.svg";           // set the image
//       // i = (i + 1) % pics.length;  // update the counter
//   }
//   setInterval(toggle, 1); 
// }; 

// console.log("progress!!")

// document.addEventListener("DOMContentLoaded", function () {

//     const fileInput = document.getElementById("image-selector");
//     const resultText = document.getElementById("displaySpan");
//     const elaImage = document.getElementById("elaImage");
//     const uploadedImage = document.getElementById("uploadedImage");
//     const changeText = document.getElementById("changeText");
//     console.log("changeText", changeText);
//     console.log('fileInput', fileInput)
//     if (!fileInput) {
//         console.error("❌ image-selector not found in HTML");
//         return;
//     }

//     fileInput.addEventListener("change", function () {
// alert('function called')
//         // if (!this.files.length) return;

//         const file = this.files[0];
// console.log('file', file)
//         const reader = new FileReader();

//         changeText.innerText = "Uploading & Analysing...";
// console.log(reader, 'reader')
//         reader.onload = function () {
// console.log('abhi main ander hoo....')
//             const base64Image = reader.result.split(",")[1];
//             console.log('base64Image', base64Image)

//             fetch("/predict", {
//                 method: "POST",
//                 headers: {
//                     "Content-Type": "application/json"
//                 },
//                 body: JSON.stringify({ image: base64Image })
//             })
//             .then(response => response.json())
//             .then(data => {

//                 // Show original image
//                 if (uploadedImage) {
//                     uploadedImage.src = reader.result;
//                     uploadedImage.style.display = "block";
//                 }

//                 // Show ELA inpur
//                 elaImage.src = data.ela_image;
//                 elaImage.style.display = "block";

//                 // Show result text
//                 resultText.innerText = data.result;
//                 changeText.innerText = "Analysis Complete";

//                 console.log("✅ Prediction:", data);
//             })
//             .catch(err => {
//                 console.error("❌ Error:", err);
//                 changeText.innerText = "Error analysing image";
//             });
//         };

//         reader.readAsDataURL(file);
//     });
// });


document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("image-selector");
    const resultText = document.getElementById("displaySpan");
    const elaImage = document.getElementById("elaImage");
    const uploadedImage = document.getElementById("uploadedImage");
    const changeText = document.getElementById("changeText");

    console.log("fileInput:", fileInput);
    console.log("changeText:", changeText);

    if (!fileInput) {
        console.error("❌ image-selector not found");
        return;
    }

    fileInput.addEventListener("change", function () {

        console.log("✅ File input change triggered");

        if (!this.files || this.files.length === 0) {
            console.warn("⚠️ No file selected");
            return;
        }

        const file = this.files[0];
        console.log("📂 Selected file:", file);

        changeText.innerText = "Uploading & Analysing...";

        const reader = new FileReader();

        reader.onload = function () {
            console.log("📖 FileReader loaded");

            const base64Image = reader.result.split(",")[1];

            console.log("📦 Base64 payload length:", base64Image.length);

            fetch("/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    image: base64Image
                })
            })
            .then(res => {
                console.log("📡 API Response status:", res.status);
                return res.json();
            })
            .then(data => {
                console.log("✅ API Result:", data);

                // Show uploaded image
                uploadedImage.src = reader.result;
                uploadedImage.style.display = "block";

                // Show ELA image
                elaImage.src = data.ela_image;
                elaImage.style.display = "block";

                // Show result text
                resultText.innerText = data.result;
                changeText.innerText = "Analysis Complete";
            })
            .catch(error => {
                console.error("❌ API Error:", error);
                changeText.innerText = "Error analysing image";
            });
        };

        reader.readAsDataURL(file);
    });
});

