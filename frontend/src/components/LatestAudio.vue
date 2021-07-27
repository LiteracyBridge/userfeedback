<template>
    <div>
        <table width="100%" class="border-separate">
            <tr> 
                <td rowspan="2" class="totalstat">
                    <span>{{context.totalReceivedMessages}}</span>
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
            <span style="text-align:left"> Filename: {{getUUID()}}</span>
            <tr><td style="padding: 10px">
                <div class="audiometadata">
                    <div v-if="url!=''">
                        <!-- for some reason this v-if has to be in this second-level div; otherwise, the audio key controls do not work.-->
                        <span style="font-weight:bold">Location:</span> {{audioMetadata.community}}, {{audioMetadata.district}}, {{audioMetadata.region}} 
                        <span class="ml-3" style="font-weight:bold"> Model:</span> {{audioMetadata.listening_model}} 
                        <span class="ml-3" style="font-weight:bold"> Group:</span> {{audioMetadata.group}} 
                        <span v-if="audioMetadata.title" style="font-weight:bold"><br/>Last message:</span> {{audioMetadata.title}} 
                    </div>
                </div>
                <div tabindex="0" class="flex justify-center noFocusOutline" ref="audioDiv" @keypress.space.prevent @keydown="checkKey">
                    <audio ref="audio" @timeupdate="checkLoop" @canplaythrough="loaded" tabindex="-1" controls preload="auto" autoplay :src="url">
                        Your browser doesn't support the HTML5 audio element.
                    </audio>
                </div>
                <div v-if="url!=''" class="audiometadata">
                    <span style="font-weight:bold">Speed:</span><span class="mr-3">  {{speed}}</span>  
                    <span v-if="this.readyToLoop()" style="font-weight:bold"> Looping  </span><span>{{loopRangeText}}</span>
                </div>
                <div v-if="url!='' && !this.fullyLoaded">
                    Loading...
                </div>
                <!-- <div style="text-align:right">
                        <button type="button" :disabled="url==''" class="button_warning" @click="$emit('handleUseless')">
                        Mark as "Not Feedback"
                        </button>
                </div> -->
              <div class="float-right">
                <v-tooltip
                  v-if="url==''"
                  text="Nothing is loaded."
                  position="right"
                  class="my-2 ml-2"
                  :width="200"
                >
                  <font-awesome-icon
                    class="text-orange-600"
                    icon="exclamation-circle"
                  />
                </v-tooltip>
                <VButton
                  label='Mark as "Not Feedback"'
                  variant="button_warning"
                  :disabled="url==''"
                  @click="$emit('handleUseless')"
                />
              </div>

            </td></tr>
        </table>
    </div>    
</template>
<script>
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'
import VButton from '@/components/VButton';
import VTooltip from '@/components/VTooltip';

Vue.use(VueAxios,axios)
var a;
export default {
    name:"LatestAudio",
    components: {
        VButton,
        VTooltip
    },
    props: ["userEmail","context"],
    connected: true,
    data() {
        return {
            audioMetadata:{
                community:'',
                district:'',
                region:'',
                listening_model:'',
                group:'',
                title:''    
            },
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
                + "&program=" + this.context.selectedProgramCode
                + "&deployment=" + this.context.selectedDeployment
                + "&language=" + this.context.selectedLanguageCode;
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
                this.audioMetadata = response.data;
                this.url=this.audioMetadata.url;
                if (this.url == '') {
                    this.$emit('no_messages');
                } else {
                    this.filename = unescape(this.url.substring(this.url.lastIndexOf('/')+1)); 
                    this.fullyLoaded = false;
                    this.$refs.audio.load();
                    this.setAudioFocus();
                }
                console.log("new URL:"+this.audioMetadata.url);
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
                case "Space":
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
table {
    border-spacing:3px;
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
