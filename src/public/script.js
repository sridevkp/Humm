const $tap = $('#tap');
const $listening = $('#listening');
const $recordBtn = $('#recordBtn');
const resultsElement = $("#result-list")

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
        $('#resultsDrawer').removeClass('show').addClass("hidden");
        setTimeout(() => {
            $listening.removeClass('hidden');
        }, 300);
        
        // Access mic
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recording = true;
    
        // Start audio analysis
        const audioContext = new AudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        const analyzer = audioContext.createAnalyser();
        analyzer.fftSize = 512; 
        analyzer.smoothingTimeConstant = 0.8; 
        source.connect(analyzer);

        const dataArray = new Uint8Array(analyzer.frequencyBinCount);
        const updatePulse = () => {
            if (!recording) return;

            analyzer.getByteTimeDomainData(dataArray); //.getByteFrequencyData 
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                const v = (dataArray[i] - 128) / 128; 
                sum += v * v;
            }
            const rms = Math.sqrt(sum / dataArray.length);
            const intensity = .8 + Math.min(rms * 20, 3);

            $recordBtn[0].style.setProperty('--pulse-intensity', intensity);

            requestAnimationFrame(updatePulse);
        };
        updatePulse();

        // Record audio  
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];      
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        // Upload on stop
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            matchAudio(audioBlob);
        };
        
        mediaRecorder.start();
        
    } catch (err) {
        alert('Could not start recording: ' + err.message);
    }
}

async function matchAudio(blob) {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');
    
    try {
        clearList()
        const result = await $.ajax({
            url: '/songs/match',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false
        });
        listResult(result)
        
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

function clearList(){
    resultsElement.empty().append([...Array(3)].map(() => $("<li>", {class:"skeleton"})));
}

function listResult(result){
    resultsElement.empty();
    if( result.matches.length == 0 ){
        const noneEl = $("<div class='empty'>:( No Matches found</div>");
        resultsElement.append(noneEl);
        return
    }
    for(const song of result.matches){
        const songEl = $(`<li>${song}</li>`,);
       resultsElement.append(songEl);
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

    $('#resultsDrawer').addClass('show').removeClass('hidden');
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

$(document).on('click', '#closeDrawer', () => {
    $('#resultsDrawer').removeClass('show');
});
