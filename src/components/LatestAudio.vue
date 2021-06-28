<template>
    <div>
        <table>
            <tr>
                <td/>
                <th>Feedback&nbsp;</th>
                <th>&nbsp;Reviewed&nbsp;</th>
                <th>&nbsp;Received</th>
            </tr>
            <tr>
                <th>Your Analysis</th>
                <td>{{users_feedback}}</td>
                <td>{{users_recordings}}</td>
                <td rowspan="2">1645</td>
            </tr>
            <tr>
                <th>Other Analysis</th>
                <td>{{others_feedback}}</td>
                <td>{{others_recordings}}</td>
            </tr>
        </table>
        <div tabindex="0" class="noFocusOutline" ref="audioDiv" @keydown="checkKey">
            <audio ref="audio" @timeupdate="checkLoop" @canplaythrough="loaded" tabindex="-1" controls preload="auto" autoplay :src="url">
                Your browser doesn't support the HTML5 audio element.
            </audio>
        </div>
        <div v-if="this.fullyLoaded">
            <span style="font-weight:bold">Location:</span> {{audioMetadata.community}}, {{audioMetadata.district}}, {{audioMetadata.region}} 
            <span style="font-weight:bold"> || Model:</span> {{audioMetadata.listening_model}} 
            <span style="font-weight:bold"> || Group:</span> {{audioMetadata.group}} 
        </div>
        <div v-if="this.fullyLoaded">
            <span style="font-weight:bold">Speed:</span>  {{speed}}  
            <span v-if="this.readyToLoop()" style="font-weight:bold"> || Looping  </span><span>{{loopRangeText}}</span>
        </div>
        <div>
        </div>
        <div v-if="!this.fullyLoaded">
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
            audioMetadata:undefined,
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
            const audioMetadataText ='{"uuid": "43b79a16-e7d5-58ea-95b1-6db1a23b7121", "region": "Afar", "district": "Leleda", "community": "Fentigera", "group": "121/1", "listening_model": "Group", "others_feedback": 2, "others_recordings": 2, "users_feedback": 3, "users_recordings": 1, "url": "https://downloads.amplio.org/e6555298-baf5-4230-8226-f2783ed15649/deployment-1/aar/43b79a16-e7d5-58ea-95b1-6db1a23b7121.mp3"}'
            this.audioMetadata = JSON.parse(audioMetadataText);
            console.log("requesting new url");
            // Vue.axios.get('https://script.google.com/macros/s/AKfycby2e2sfOQGYb1SATDrhtUXf8dAEvMmbylQYyHiEdx3aF7oOX983xcG0EQ-Jbc_WHI73iQ/exec')
            // .then(response=>{
                this.url=this.audioMetadata.url;
                this.filename = unescape(this.url.substring(this.url.lastIndexOf('/')+1)); 
                this.fullyLoaded = false;
                this.$refs.audio.load();
                this.setAudioFocus();
                console.log("new URL:"+this.audioMetadata.url);
            // })
        },
        submitUrl() {
            const payload = "url="+this.url;
            console.log("sending: ", payload);
            // Vue.axios.get('https://script.google.com/macros/s/AKfycby2e2sfOQGYb1SATDrhtUXf8dAEvMmbylQYyHiEdx3aF7oOX983xcG0EQ-Jbc_WHI73iQ/exec?'+payload)
            // .then(response =>{
            //    console.log("response: ",response);
            // })
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
        a = this.$refs.audio;
        if(this.$route.path=='/app') {
            this.updateUrl();
        }
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
        },
        others_feedback() {
            var resp="";
            if (this.audioMetadata) {
                resp = this.audioMetadata.others_feedback;
            }
            return resp;
        },
        others_recordings() {
            var resp="";
            if (this.audioMetadata) {
                resp = this.audioMetadata.others_recordings;
            }
            return resp;
        },
        users_feedback() {
            var resp="";
            if (this.audioMetadata) {
                resp = this.audioMetadata.users_feedback;
            }
            return resp;
        },
        users_recordings() {
            var resp="";
            if (this.audioMetadata) {
                resp = this.audioMetadata.users_recordings;
            }
            return resp;
        }
    }
}
</script>
<style scoped>
.noFocusOutline {
    outline: 0px solid transparent;
}
td {
  text-align: center;
}
</style>
