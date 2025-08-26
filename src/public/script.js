const $tap = $('#tap');
const $listening = $('#listening');
const $recordBtn = $('#recordBtn');

let mediaRecorder, audioChunks = [];
let recording = false;

async function startRecording() {

    if (!navigator.mediaDevices) {
        alert('Audio recording not supported in this browser.');
        return;
    }
    try {
        $tap.addClass('hidden');
        $recordBtn.addClass('recording');
        setTimeout(() => {
            $listening.removeClass('hidden');
        }, 300);
        
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            uploadAudio(audioBlob);
        };
        
        mediaRecorder.start();
        recording = true;
        
    } catch (err) {
        alert('Could not start recording: ' + err.message);
    }
}

async function uploadAudio(blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');
    
    try {
        const result = await $.ajax({
            url: '/songs/match',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });
        console.log('Server response:', result);
        
        if (result.redirect) {
            window.location.href = result.redirect;
        }
    } catch (err) {
       console.error('Upload failed:', err); 
    } finally {
        audioChunks = [];
        mediaRecorder = null;
    }
}

function stopRecording() {
    if (! mediaRecorder ||  !recording) return ;
    
    mediaRecorder.stop();
    recording = false;
    
    $listening.addClass('hidden');
    $recordBtn.removeClass('recording');
    setTimeout(() => {
        $tap.removeClass('hidden');
    }, 300);    
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
