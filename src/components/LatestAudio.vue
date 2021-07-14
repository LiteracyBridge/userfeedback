<template>
    <div>
        <table width="100%">
            <tr> 
                <td rowspan="2" class="totalstat">
                    <span>{{totalReceivedMessages}}</span>
                    <br/>
                    <span>Total received</span>
                </td>

                <td class="stats">
                    <span>{{users_analyzed}}</span>
                    <span>Analyzed by you</span>
                </td>
                <td class="stats">
                    <span>{{users_feedback}}</span>
                    <span>Feedback</span>
                </td>
                <td class="stats">
                    <span>{{users_notFeedback}}</span>
                    <span>Not Feedback</span>
                </td>
            </tr>
            <tr>
                <td class="stats">
                    <span>{{total_analyzed}}</span>                    
                    <span>Total Analyzed</span>
                </td>
                <td class="stats">
                    <span>{{total_feedback}}</span>
                    <span>Total Feedback</span>
                </td>
                <td class="stats">
                    <span>{{total_notFeedback}}</span>
                    <span>Total Not Feedback</span>
                </td>
            </tr>
        </table>
        <br/>
        Audio Player
        <table style="border: 2px solid #ddd" width="100%">
            <tr><td style="padding: 10px">
                <span class="audiometadata">Filename: {{getUUID()}}</span>
                <div tabindex="0" class="noFocusOutline" ref="audioDiv" @keydown="checkKey">
                    <audio ref="audio" @timeupdate="checkLoop" @canplaythrough="loaded" tabindex="-1" controls preload="auto" autoplay :src="url">
                        Your browser doesn't support the HTML5 audio element.
                    </audio>
                </div>
                <div v-if="this.fullyLoaded" class="audiometadata">
                    <span style="font-weight:bold">Location:</span> {{audioMetadata.community}}, {{audioMetadata.district}}, {{audioMetadata.region}} 
                    <span style="font-weight:bold"> || Model:</span> {{audioMetadata.listening_model}} 
                    <span style="font-weight:bold"> || Group:</span> {{audioMetadata.group}} 
                </div>
                <div v-if="this.fullyLoaded" class="audiometadata">
                <!-- <div> -->
                    <span style="font-weight:bold">Speed:</span>  {{speed}}  
                    <span v-if="this.readyToLoop()" style="font-weight:bold"> || Looping  </span><span>{{loopRangeText}}</span>
                </div>
                <div v-if="!this.fullyLoaded">
                    Loading...
                </div>
                <div style="text-align:right">
                        <button type="button" class="button_warning" @click="$emit('handleUseless')">
                        Mark as "Not Feedback"
                        </button>
                </div>
            </td></tr>
        </table>
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
    props: ["userEmail","program","deployment","language","totalReceivedMessages"],
    connected: true,
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
            const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufDataService?"
                + "email=" + this.userEmail
                + "&program=" + this.program
                + "&deployment=" + this.deployment
                + "&language=" + this.language;
            // Vue.axios.interceptors.request.use(request => {
            //     console.log('Starting Request', JSON.stringify(request, null, 2))
            //     return request
            // });
            Vue.axios.get(request,{headers: {'Authorization': `${this.$token}`}})
            .then(response=>{
                if (!this.connected) {
                    this.$emit('network',true);
                    this.connected = true;
                }
                if (Object.keys(response.data).length == 0) {
                    this.$emit('no_messages');
                } else {
                    this.audioMetadata = response.data;
                    this.url=this.audioMetadata.url;
                    this.filename = unescape(this.url.substring(this.url.lastIndexOf('/')+1)); 
                    this.fullyLoaded = false;
                    this.$refs.audio.load();
                    this.setAudioFocus();
                    console.log("new URL:"+this.audioMetadata.url);
                }
            }).catch(err => {
                console.log("caught:"+err)
                this.$emit('network',false);
                this.connected = false;
            })
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
        },
        getUUID() {
            if (this.audioMetadata)
                return this.audioMetadata.uuid;
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
        total_analyzed() {
            var resp="";
            if (this.audioMetadata) {
                return this.audioMetadata.others_recordings + this.audioMetadata.users_recordings;
            }
        },
        total_feedback() {
            var resp="";
            if (this.audioMetadata) {
                return this.audioMetadata.others_feedback + this.audioMetadata.users_feedback;
            }
        },
        total_notFeedback() {
            var resp="";
            if (this.audioMetadata) {
                return this.total_analyzed - this.total_feedback;
            }
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
        users_analyzed() {
            var resp="";
            if (this.audioMetadata) {
                resp = this.audioMetadata.users_recordings;
            }
            return resp;
        },
        users_notFeedback() {
            var resp="";
            if (this.audioMetadata) {
                return this.audioMetadata.users_recordings - this.audioMetadata.users_feedback;
            }
        }
    }
}
</script>

<style scoped>
.audiometadata {
    font-size: 0.80em;
}
.noFocusOutline {
    outline: 0px solid transparent;
}
td {
    text-align:center;
}
td.stats {
    text-align:left;
    background-color:lightgray;
    padding:8px;
    line-height: 20px;
}
td.stats span:first-child{
    float:left;
    font-weight: bolder;
    font-size: 1.25em;
    vertical-align:middle;
}
td.stats span:last-child{
    float:right;
    font-size: 0.85em; 
    vertical-align:middle;
}
td.totalstat {
    vertical-align: middle;
    text-align:center;
    padding:10px;
    font-weight: bold;
}
td.totalstat span:first-child{
    font-weight: bolder;
    font-size: 1.15em;
}

.button_warning {
  border: none;
  color: #FFF;
  background: red;
  appearance: none;
  font: inherit;
  font-size: 1.2rem;
  font-weight:bolder;
  padding: .5em 1em;
  border-radius: .3em;
  cursor: pointer;
}


</style>
