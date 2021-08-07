<template>
    <div>
        <table width="100%" class="border-separate">
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
    </div>
</template>
<script>
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'

Vue.use(VueAxios,axios)

export default {
    name:"Stats",
    props: ["progress"],
    data() {
        return {
        }
    },
    methods: {

    },
    computed: {
        totalReceivedMessages() {
            var resp="";
            if (this.progress) {
                resp= this.progress.totalReceivedMessages;
            }
            return resp;
        },
        total_analyzed() {
            var resp="";
            if (this.progress) {
                resp = this.progress.others_recordings + this.progress.users_recordings;
            }
            return resp;
        },
        total_feedback() {
            var resp="";
            if (this.progress) {
                resp = this.progress.others_feedback + this.progress.users_feedback;
            }
            return resp;
        },
        total_notFeedback() {
            var resp="";
            if (this.progress) {
                resp = this.total_analyzed - this.total_feedback;
            }
            return resp;
        },
        others_feedback() {
            var resp="";
            if (this.progress) {
                resp = this.progress.others_feedback;
            }
            return resp;
        },
        others_recordings() {
            var resp="";
            if (this.progress) {
                resp = this.progress.others_recordings;
            }
            return resp;
        },
        users_feedback() {
            var resp="";
            if (this.progress) {
                resp = this.progress.users_feedback;
            }
            return resp;
        },
        users_analyzed() {
            var resp="";
            if (this.progress) {
                resp = this.progress.users_recordings;
            }
            return resp;
        },
        users_notFeedback() {
            var resp="";
            if (this.progress) {
                resp = this.progress.users_recordings - this.progress.users_feedback;
            }
            return resp;
        }
    }
}
</script>

<style scoped>
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
</style>