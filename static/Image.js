const loadedImages = new Set();
const container = document.getElementById('container');
const background = document.getElementById('background');
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');
const history = [];
let selectedOverlay = null;
let overlayHistory = [];
let overlayHistoryIndex = -1;

const positions = [
    { top: '0%', left: '0%' },   
    { top: '0%', left: '33%' },  
    { top: '0%', left: '66%' },  
    { top: '33%', left: '0%' },   
    { top: '33%', left: '33%' },  
    { top: '33%', left: '66%' },  
    { top: '66%', left: '0%' },   
    { top: '66%', left: '33%' },  
    { top: '66%', left: '66%' }
];

function loadNewImage() {
    fetch('/images')
        .then(response => response.json())
        .then(data => {
            data.images.forEach(image => {
                if (loadedImages.has(image)) {  
                    return;
                }
                loadedImages.add(image);

                const img = document.createElement('img');
                img.classList.add('overlay');
                img.src = '/processed/' + image;

                img.style.width = (background.clientWidth / 2) + 'px';
                img.style.height = 'auto';

                img.style.top = '0px';  
                img.style.left = '0px';
                
                img.onclick = () => selectOverlay(img);  
                container.appendChild(img);
            });
        })
        .catch(error => {
            console.error(error);
            document.getElementById('error').innerText = 'Error: ' + error.message;
        });
}

function resizeOverlay(scaleFactor) {
    if (selectedOverlay) {
        selectedOverlay.style.transform = 'scale(' + scaleFactor + ')';
    }
}
window.addEventListener('keydown', (e) => {
    if (!selectedOverlay) return;

    const key = parseInt(e.key);
    if (key >= 1 && key <= 9) {
        const bgWidth = background.clientWidth;
        const bgHeight = background.clientHeight;
        
        
        const cols = 3;
        const rows = 3;
        const cellWidth = bgWidth / cols;
        const cellHeight = bgHeight / rows;
        const col = (key - 1) % cols;
        const row = Math.floor((key - 1) / rows);

    
        const overlayX = col * cellWidth;
        const overlayY = row * cellHeight;
        selectedOverlay.style.left = `${overlayX}px`;
        selectedOverlay.style.top = `${overlayY}px`;
    }


    if (e.key === '+') {
        selectedOverlay.style.width = selectedOverlay.clientWidth * 1.1 + "px";  
        selectedOverlay.style.height = "auto";  
    }
    if (e.key === '-') {
        selectedOverlay.style.width = selectedOverlay.clientWidth * 0.9 + "px";  
        selectedOverlay.style.height = "auto";  
    }
    if (e.key === 'Enter') { 
        if (selectedOverlay) {
            selectedOverlay.style.border = 'none'; 
            selectedOverlay = null; 
        }
        return;
    }
});

async function saveImage() {
    const filterSelect = document.getElementById('filterOptions');
    const selectedFilter = filterSelect.value; // 사용자가 선택한 필터 값을 가져옵니다.

    const canvas = document.createElement('canvas');
    canvas.width = background.clientWidth; 
    canvas.height = background.clientHeight; 
    const ctx = canvas.getContext('2d');

    ctx.filter = selectedFilter; // 선택된 필터 값을 캔버스에 적용합니다.

    ctx.drawImage(background, 0, 0, canvas.width, canvas.height);

    const overlays = document.querySelectorAll('.overlay');
    overlays.forEach(overlay => {
        const transform = overlay.style.transform;
        const top = overlay.offsetTop;
        const left = overlay.offsetLeft;
        const width = overlay.clientWidth;
        const height = overlay.clientHeight;

        ctx.save();
        ctx.translate(left + width / 2, top + height / 2);
        ctx.rotate(parseFloat(transform.replace('rotate(', '').replace('deg)', '')) * Math.PI / 180);
        ctx.drawImage(overlay, -width / 2, -height / 2, width, height);
        ctx.restore();
    });

    const dataUrl = canvas.toDataURL('image/png');

    try {
        const response = await fetch('/save-image', {
            method: 'POST',
            body: dataURItoBlob(dataUrl), 
            headers: { 'Content-Type': 'image/png' }
        });

        if (response.ok) {
            const result = await response.json();
            console.log(result.message); 
        } else {
            console.error('Failed to save image');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function selectOverlay(overlay) {
    if (selectedOverlay) {
        if (selectedOverlay === overlay) {  
            selectedOverlay.style.border = '2px solid red';
            return;
        } else {
            selectedOverlay.style.border = 'none';  
        }
    }

    selectedOverlay = overlay;
    selectedOverlay.style.border = '2px solid red';  
}


setInterval(loadNewImage, 5000);


function dataURItoBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const buffer = new Uint8Array(byteString.length);
    for (let i = 0; i < byteString.length; i++) {
        buffer[i] = byteString.charCodeAt(i);
    }
    return new Blob([buffer], { type: mimeString });
}


function saveState() {
    if (!selectedOverlay) return;

    overlayHistoryIndex++;
    overlayHistory[overlayHistoryIndex] = {
        transform: selectedOverlay.style.transform,
        top: selectedOverlay.style.top,
        left: selectedOverlay.style.left,
        width: selectedOverlay.style.width
    };

    overlayHistory.length = overlayHistoryIndex + 1;
    console.log('Saved state', overlayHistory[overlayHistoryIndex]);
}

function undo() {
    console.log('Undoing');

    if (overlayHistoryIndex <= 0) return;
    overlayHistoryIndex--;

    const previousState = overlayHistory[overlayHistoryIndex];
    applyOverlayState(previousState);
}

function redo() {
    console.log('Redoing');

    if (overlayHistoryIndex >= overlayHistory.length - 1) return;
    overlayHistoryIndex++;

    const nextState = overlayHistory[overlayHistoryIndex];
    applyOverlayState(nextState);
}

function applyOverlayState(state) {
    if (!selectedOverlay || !state) return;

    selectedOverlay.style.transform = state.transform;
    selectedOverlay.style.top = state.top;
    selectedOverlay.style.left = state.left;
    selectedOverlay.style.width = state.width;
}

function rotate() {
    if (!selectedOverlay) return;  

    const angleInput = document.getElementById('rotateAngle');
    const angle = parseInt(angleInput.value);  

    if (isNaN(angle)) {  
        console.error("Please enter a valid angle.");  
        return;
    }

    const currentRotation = selectedOverlay.style.transform || 'rotate(0deg)';
    const currentAngle = parseInt(currentRotation.replace('rotate(', '').replace('deg)', '')) || 0;
    const newAngle = currentAngle + angle;  

    selectedOverlay.style.transform = `rotate(${newAngle}deg)`;  
    saveState();  
}

window.rotateImage = function(degrees) {
    console.log('Rotating image by', degrees, 'degrees');
    if (isNaN(degrees)) {
        console.error("Invalid input. Please enter a number.");
        return;
    }

    const image = new Image();
    image.src = canvas.toDataURL();
    image.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate((degrees * Math.PI) / 180);
        ctx.drawImage(image, -image.width / 2, -image.height / 2);
        ctx.restore();
        saveState();  
    };
};

function applySelectedFilter() {
    const filterSelect = document.getElementById('filterOptions');
    const selectedFilter = filterSelect.value; 
    console.log("Selected Filter:", selectedFilter);
    applyFilter(selectedFilter);
}

function applyDirectFilter() {
    const filterSelect = document.getElementById('filterOptions');
    const selectedFilter = filterSelect.value;
    background.style.filter = selectedFilter;  // 배경 이미지에 필터 적용

    const overlays = document.querySelectorAll('.overlay');
    overlays.forEach(overlay => {
        overlay.style.filter = selectedFilter;  // 오버레이 이미지에 필터 적용
    });
}


const layerPanel = document.getElementById('layerPanel');

function addLayer(name) {
    const layerItem = document.createElement('div');
    layerItem.textContent = name;
    layerPanel.appendChild(layerItem);
}