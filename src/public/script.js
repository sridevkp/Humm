const $recordBtn = $('#recordBtn');
const $statusMessage = $('#statusMessage');
let mediaRecorder, audioChunks = [];
let recording = false;
let audioContext, analyser, dataArray;

async function startRecording() {
    if (!navigator.mediaDevices) {
        alert('Audio recording not supported in this browser.');
        return;
    }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        // Set up audio analysis
        audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        dataArray = new Uint8Array(analyser.frequencyBinCount);
        
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            uploadAudio(audioBlob);
        };
        
        mediaRecorder.start();
        recording = true;
        $recordBtn.removeClass().addClass("icon stop")
        
        updateShadow();
    } catch (err) {
        alert('Could not start recording: ' + err.message);
    }
}

function updateShadow() {
    if (!recording) return;
    
    analyser.getByteFrequencyData(dataArray);
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    const scale = 1.05 + (average / 512);
    const shadow = Math.min(48, 24 + average / 4);
    
    $recordBtn.css({
        transform: `scale(${scale})`,
        boxShadow: `0 ${shadow}px ${shadow * 2}px 0 rgba(255, 95, 109, 0.5), 
                    0 4px 16px 0 rgba(0,0,0,0.18), 
                    0 3px 0 #fff inset`
    });
    
    requestAnimationFrame(updateShadow);
}

async function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');
    
    $recordBtn.addClass('loading');
    $statusMessage.text('Uploading recording...');
    
    try {
        const result = await $.ajax({
            url: '/audio/save',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });
        
        if (result.redirect) {
            window.location.href = result.redirect;
        } else {
            $statusMessage.text('Upload successful!');
        }
    } catch (err) {
        $statusMessage.text('Upload failed: ' + err.message);
    } finally {
        $recordBtn.removeClass('loading');
    }
}

function stopRecording() {
    if (mediaRecorder && recording) {
        mediaRecorder.stop();
        recording = false;
        $recordBtn.removeClass().addClass('icon start');
            
        if (audioContext) {
            audioContext.close();
        }
    }
}

$(document).ready(() => {
    $recordBtn.on('click', () => {
        if (!recording) {
            startRecording();
        } else {
            stopRecording();
        }
    });
});
