<template>
    <div>
<!--    <p>
            <a tabindex="-1" :href="url" target="_blank">{{filename}}</a>
        </p>  
-->
        <div tabindex="0" class="noFocusOutline" ref="audioDiv" @keydown="checkKey">
            <audio ref="audio" @timeupdate="checkLoop" @canplaythrough="loaded" tabindex="-1" controls preload="auto" autoplay :src="url">
                Your browser doesn't support the HTML5 audio element.
            </audio>
        </div>
        <div>
            <span v-if="this.readyToLoop()">Looping  </span><span>{{loopRangeText}}</span>
        </div>
        <div v-if="this.fullyLoaded">
            Speed: {{speed}}  
        </div>
        <div v-else>
            Loading...
        </div>
    </div>    
</template>
<script>
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'
Vue.use(VueAxios,axios)
var a;
export default {
    name:"LatestAudio",
    data() {
        return {
            url:undefined,
            speed:1,
            fullyLoaded:false,
            loopStart:0,
            loopEnd:0,
            inLoop:false,
            filename:undefined,
            }
    },
    methods: {
        loaded() {
            this.fullyLoaded=true;
        },
        increaseSpeed() {
            if (this.speed < 2) {
                this.speed += 0.25;
                a.playbackRate = this.speed;
            }
        },
        decreaseSpeed() {
            if(this.speed >= 0.5) {
                this.speed -= 0.25;
                a.playbackRate = this.speed;
            }
        },
        playPause() {
            if(this.fullyLoaded) {
                if (a.paused) {
                    a.play();
                } else {
                    a.pause();
                }
            }            
        },
        seekForward() {
            if(this.fullyLoaded) {
                a.currentTime += 10; 
                if(a.paused) {
                    a.play();
                }
            }
        },
        seekBackward() {
            if (this.fullyLoaded) {
                a.currentTime -= 10; 
                if(a.paused) {
                    a.play();
                }
            }
        },
        seekQuickRepeat() {
            if (this.fullyLoaded) {
                a.currentTime -= 5; 
                if(a.paused) {
                    a.play();
                }
            }                
        },
        updateUrl() {
            console.log("requesting new url");
            Vue.axios.get('https://script.google.com/macros/s/AKfycby2e2sfOQGYb1SATDrhtUXf8dAEvMmbylQYyHiEdx3aF7oOX983xcG0EQ-Jbc_WHI73iQ/exec')
            .then(response=>{
                this.url=response.data;
                this.filename = unescape(this.url.substring(this.url.lastIndexOf('/')+1)); 
                this.fullyLoaded = false;
                this.$refs.audio.load();
                this.setAudioFocus();
                console.log("new URL:"+response);
            })
        },
        submitUrl() {
            const payload = "url="+this.url;
            console.log("sending: ", payload);
            Vue.axios.get('https://script.google.com/macros/s/AKfycby2e2sfOQGYb1SATDrhtUXf8dAEvMmbylQYyHiEdx3aF7oOX983xcG0EQ-Jbc_WHI73iQ/exec?'+payload)
            .then(response =>{
                console.log("response: ",response);
            })
        },
        submitAndUpdate() {
            //deal with this form submission test later: this.submitUrl();
            this.updateUrl();
        },
        readyToLoop() {
            return  (this.loopEnd >0);  // If we want Start set explictly then add: && this.loopStart>0
        },
        checkLoop() {
            //inLoop is used to prevent skipping from multiple timeupdate events
            if(this.inLoop && this.readyToLoop() && !a.paused) {
                if(a.currentTime > this.loopEnd) {
                    this.inLoop = false;
                    this.startLoop(false);
                }
            }
        },
        startLoop(setStart) {
            if (this.readyToLoop()) {
                if (!setStart) {
                    a.currentTime = this.loopStart;
                }
                if (a.paused) {
                    a.play();
                }
                this.inLoop = true;
            }
        },
        stopLoop() {
            this.loopStart = 0;
            this.loopEnd = 0;
            this.inLoop = false;
        },
        checkKey(e) {
            switch(e.code) {
                case "KeyP":
                    this.playPause();
                    break;
                case "KeyF":
                case "KeyI":
                    this.increaseSpeed();
                    console.log("speed:",this.speed);
                    break;
                case "KeyS":
                case "KeyM":
                    this.decreaseSpeed();
                    console.log("speed:",this.speed);
                    break;
                case "ArrowRight":
                case "KeyK":
                    console.log("seek fwd");
                    this.seekForward();
                    break;
                case "ArrowLeft":
                case "KeyJ":
                    console.log("seek back");
                    this.seekBackward();
                    break;
                case "Slash":
                case "KeyH":
                    this.seekQuickRepeat();
                    break;
                case "BracketLeft":
                    this.loopStart = a.currentTime;
                    this.startLoop(true);
                    break;
                case "BracketRight":
                    this.loopEnd = a.currentTime;
                    this.startLoop(false);
                    break;
                case "Backslash":
                    this.stopLoop();
                    break;
                case "Backspace":
                    // confirm that the audio is useless
                    break;
                default:
                    console.log(e.code);
            }
        },
        setAudioFocus() {
            this.$refs.audioDiv.focus();
        },
        getMinSecText(time) {
            var min = Math.trunc(time/60);
            var sec = Math.round(time - min*60);
            return String(min) + ":" + String(sec).padStart(2,"0");
        }
    },
    mounted() {
        this.updateUrl();
        a = this.$refs.audio;
    },
    computed: {
        audioUrl() {
            return this.url;
        },
        loopRangeText() {
            var s="";
            if(this.loopStart || this.loopEnd) {
                s="Start: "+this.getMinSecText(this.loopStart) + "   ";
                if (this.loopEnd > 0) {
                    s+="End: "+this.getMinSecText(this.loopEnd);
                }
            }
            return s;
        }
    }
}
</script>
<style scoped>
.noFocusOutline {
    outline: 0px solid transparent;
}
</style>
