/* ==========================================================
   TIMER ENGINE & WEB AUDIO ALERTS
   ========================================================== */

class ExtemporeTimer {
    constructor() {
        this.timerInterval = null;
        this.totalDuration = 0;
        this.timeRemaining = 0;
        this.onTick = null;
        this.onComplete = null;
        this.audioCtx = null;
    }

    initAudio() {
        if (!this.audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.audioCtx = new AudioContext();
            }
        }
    }

    playBeep(frequency = 600, duration = 0.15, type = 'sine') {
        try {
            this.initAudio();
            if (!this.audioCtx) return;
            if (this.audioCtx.state === 'suspended') {
                this.audioCtx.resume();
            }
            const osc = this.audioCtx.createOscillator();
            const gain = this.audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(frequency, this.audioCtx.currentTime);
            
            gain.gain.setValueAtTime(0.15, this.audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + duration);

            osc.connect(gain);
            gain.connect(this.audioCtx.destination);

            osc.start();
            osc.stop(this.audioCtx.currentTime + duration);
        } catch (e) {
            console.log('Audio alert notification notice:', e);
        }
    }

    start(durationSeconds, onTick, onComplete) {
        this.stop();
        this.totalDuration = durationSeconds;
        this.timeRemaining = durationSeconds;
        this.onTick = onTick;
        this.onComplete = onComplete;

        this.initAudio();

        if (this.onTick) {
            this.onTick(this.timeRemaining, this.totalDuration);
        }

        const startTime = Date.now();
        const expectedEndTime = startTime + (durationSeconds * 1000);

        this.timerInterval = setInterval(() => {
            const now = Date.now();
            const diffMs = expectedEndTime - now;
            this.timeRemaining = Math.max(0, Math.ceil(diffMs / 1000));

            // Sound alerts for final 5 seconds
            if (this.timeRemaining <= 5 && this.timeRemaining > 0) {
                this.playBeep(520, 0.12, 'sine');
            } else if (this.timeRemaining === 0) {
                this.playBeep(880, 0.4, 'triangle');
            }

            if (this.onTick) {
                this.onTick(this.timeRemaining, this.totalDuration);
            }

            if (this.timeRemaining <= 0) {
                this.stop();
                if (this.onComplete) {
                    this.onComplete();
                }
            }
        }, 250);
    }

    stop() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    getTimeTaken() {
        return this.totalDuration - this.timeRemaining;
    }

    static formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

window.ExtemporeTimer = ExtemporeTimer;
