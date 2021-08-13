<template>
    <div>
        <span style="float:left;font-weight:bold">Audio Player</span>
        <table style="border: 2px solid #ddd" width="100%">
            <span style="float:left"> Filename: {{getUUID()}}</span>
            <tr><td style="padding: 10px">
                <div class="audioMetadata">
                    <div v-if="audioMetadata.title">
                        <span style="font-weight:bold">Last message:</span> {{audioMetadata.title}} 
                    </div>
                    <div v-else><br/></div>
                    <div v-if="audioMetadata.url!=''">
                        <!-- for some reason this v-if has to be in this second-level div; otherwise, the audio key controls do not work.-->
                        <span style="font-weight:bold">Location:</span> {{audioMetadata.community}}, {{audioMetadata.district}}, {{audioMetadata.region}} 
                        <span class="ml-3" style="font-weight:bold"> Model:</span> {{audioMetadata.listening_model}} 
                        <span class="ml-3" style="font-weight:bold"> Group:</span> {{audioMetadata.group}} 
                    </div>
                </div>
                <div tabindex="0" class="flex justify-center noFocusOutline" ref="audioDiv" @keypress.space.prevent @keydown="checkKey">
                    <audio ref="audio" @timeupdate="checkLoop" @error="loadError" @canplaythrough="loaded" tabindex="-1" controls preload="auto" autoplay :src="audioMetadata.url">
                        Your browser doesn't support the HTML5 audio element.
                    </audio>
                </div>
                <div v-if="audioMetadata.url!=''" class="audiometadata">
                    <span style="font-weight:bold">Speed:</span><span class="mr-3">  {{speed}}</span>  
                    <span v-if="this.readyToLoop()" style="font-weight:bold"> Looping  </span><span>{{loopRangeText}}</span>
                </div>
                <div v-if="audioMetadata.url!='' && !this.fullyLoaded">
                    Loading...
                </div>
            </td></tr>
            <span v-if="audioMetadata.submission" class="relative right-0 float-right mb-2 mr-5">
                <button class="button" @click="$emit('next')">Skip</button>
            </span>
        </table>
    </div>    
</template>
<script>
var a;
export default {
    name:"AudioPlayer",
    props: ["audioMetadata"],
    data() {
      return {
        connected: true,
        // audioMetadata:{
        //     community:'',
        //     district:'',
        //     region:'',
        //     listening_model:'',
        //     group:'',
        //     title:''    
        // },
        speed:1,
        fullyLoaded:false,
        loopStart:0,
        loopEnd:0,
        inLoop:false,
      }
    },
    methods: {
        loadError() {
            if (this.audioMetadata.url != 'url') {
                if (this.$refs.audio.error.code==4) {
                    console.log("missing mp3");
                    this.$emit("srcError",false);
                }
            }
        },
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
        if(this.$route.path=='/analyze' || this.$route.path=='/responses') {
            this.fullyLoaded = false;
            this.$refs.audio.load();
            this.setAudioFocus();
        }
    },
    computed: {
        audioUrl() {
            return this.audioMetadata.url;
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
.audioMetadata {
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
th {
  text-align: right;
  /* border-bottom: 1px solid #ddd; */
}
</style>
