const socket = io.connect("http://" + document.domain + ":" + location.port);

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const alarmsList = document.getElementById("alarmsList");
const toggleButton = document.getElementById("toggleCamera");
const uploadForm = document.getElementById("uploadForm");
const videoInput = document.getElementById("videoUpload");

let streaming = false;
let stream = null;
let sendFrameInterval = null;
let userEmail = "";

function saveEmail() {
    const emailInput = document.getElementById("userEmail");
    const modal = document.getElementById("sessionModal");
    if (emailInput.value) {
        userEmail = emailInput.value;
        modal.style.display = "none";
    } else {
        alert("Por favor, insira um e-mail válido.");
    }
}

// Ligar ou desligar câmera
toggleButton.addEventListener("click", async () => {
    if (!streaming) {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            streaming = true;
            toggleButton.textContent = "Desligar Câmera";

            sendFrameInterval = setInterval(() => {
                captureFrame();
            }, 300); // Ajuste o intervalo conforme necessário
        } catch (err) {
            console.error("Erro ao acessar a câmera:", err);
        }
    } else {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        clearInterval(sendFrameInterval);
        streaming = false;
        toggleButton.textContent = "Ligar Câmera";
    }
});

// Captura o frame e envia ao servidor
function captureFrame() {
    if (!streaming) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataURL = canvas.toDataURL("image/jpeg");
    socket.emit("frame", { 
        image: dataURL,
        email: userEmail
    });
}

// Recebe evento de alarme
socket.on("alarm", (data) => {
    addAlarmToList(data);
});

// Adiciona alarme à lista
function addAlarmToList(alarmData) {
    const alarmsList = document.getElementById("alarmsList");

    const alarmDiv = document.createElement("div");
    alarmDiv.className = "alarmItem";

    const img = document.createElement("img");
    img.src = alarmData.image;
    img.alt = "Alarme";
    img.onclick = () => showModal(alarmData.image, alarmData.timestamp, alarmData.message);

    const info = document.createElement("div");
    info.innerHTML = `<strong>${alarmData.timestamp}</strong><br>${alarmData.message}`;

    alarmDiv.appendChild(img);
    alarmDiv.appendChild(info);
    alarmsList.appendChild(alarmDiv);
}

// Modal functions
function showModal(imageBase64, timestamp, message) {
    const modal = document.getElementById("alarmModal");
    const modalImg = document.getElementById("modalImage");
    const caption = document.getElementById("modalCaption");

    modal.style.display = "block";
    modalImg.src = imageBase64;
    caption.innerHTML = `<strong>${timestamp}</strong><br>${message}`;
}

function closeModal() {
    document.getElementById("alarmModal").style.display = "none";
}

// Upload de vídeo
uploadForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const file = videoInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("video", file);
    formData.append("email", userEmail);

    fetch("/upload", {
        method: "POST",
        body: formData,
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    })
    .catch(err => {
        console.error("Erro ao enviar vídeo:", err);
        alert("Erro ao processar vídeo.");
    });
});
