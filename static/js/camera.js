document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const captureButton = document.getElementById("capture");
  const resultImage = document.getElementById("result");

  // Access the camera and display the video stream
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
      video.play();
    })
    .catch((err) => {
      console.error("Error accessing camera:", err);
    });

  // Capture an image when the button is clicked
  captureButton.addEventListener("click", () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    // Convert the captured image to a base64-encoded data URL
    const imageDataUrl = canvas.toDataURL("image/jpeg");

    // Send the image data to the Flask server for object detection
    fetch("/detect_objects", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `image=${encodeURIComponent(imageDataUrl)}`,
    })
      .then((response) => response.json())
      .then((results) => {
    // Process the results and display them on the page
    results.forEach((result) => {
      const { class_name, confidence, bbox } = result;
      const [x, y, w, h] = bbox;
    
      // Scale the bounding box coordinates back to the original size
      const scaledX = x;
      const scaledY = y;
      const scaledW = w;
      const scaledH = h; 
    
      // Draw the bounding box
      ctx.strokeStyle = "red";
      ctx.lineWidth = 2;
      ctx.strokeRect(scaledX, scaledY, scaledW, scaledH);
    
      // Draw the label
      const label = `${class_name} (${Math.round(confidence * 100)}%)`;
      ctx.fillStyle = "red";
      ctx.font = "14px sans-serif";
      ctx.fillText(label, scaledX + 2, scaledY + 14);
    });
        // Convert the updated canvas to a base64-encoded data URL and set it as the result image source
        resultImage.src = canvas.toDataURL("image/jpeg");
      })
      .catch((err) => {
        console.error("Error detecting objects:", err);
      });
  });
});
