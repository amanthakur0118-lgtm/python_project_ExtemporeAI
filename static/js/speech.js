/* ==========================================================
   SPEECH-TO-TEXT (VOICE INPUT) & WAVEFORM MANAGER
   ========================================================== */

class SpeechInputManager {
    constructor(onTranscriptCallback, onStateChangeCallback) {
        this.recognition = null;
        this.isRecording = false;
        this.onTranscript = onTranscriptCallback;
        this.onStateChange = onStateChangeCallback;
        this.initRecognition();
    }

    isSupported() {
        return ('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window);
    }

    initRecognition() {
        if (!this.isSupported()) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isRecording = true;
            if (this.onStateChange) this.onStateChange(true);
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript + ' ';
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (this.onTranscript) {
                this.onTranscript(finalTranscript, interimTranscript);
            }
        };

        this.recognition.onerror = (event) => {
            console.log('Speech recognition notice:', event.error);
            if (event.error === 'not-allowed') {
                alert('Microphone access was denied. Please allow microphone permissions in your browser or type your answer.');
                this.stop();
            }
        };

        this.recognition.onend = () => {
            if (this.isRecording) {
                // If it ended unexpectedly while user wanted to record, restart
                try {
                    this.recognition.start();
                } catch(e) {
                    this.isRecording = false;
                    if (this.onStateChange) this.onStateChange(false);
                }
            } else {
                if (this.onStateChange) this.onStateChange(false);
            }
        };
    }

    start() {
        if (!this.isSupported()) {
            alert('Your browser does not natively support the Web Speech API. Please use Chrome, Edge, or type directly into the editor.');
            return;
        }
        if (this.isRecording) return;
        try {
            this.isRecording = true;
            this.recognition.start();
        } catch (e) {
            console.log('Error starting recognition:', e);
        }
    }

    stop() {
        if (!this.recognition) return;
        this.isRecording = false;
        try {
            this.recognition.stop();
        } catch (e) {}
        if (this.onStateChange) this.onStateChange(false);
    }

    toggle() {
        if (this.isRecording) {
            this.stop();
        } else {
            this.start();
        }
    }
}

window.SpeechInputManager = SpeechInputManager;
