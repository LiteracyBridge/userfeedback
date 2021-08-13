<template>
  <div ref="top">
    <div>
    <span style="float:left; font-weight:bold">Feedback Form</span>
    </div>
    <table width="100%" style="text-align:left;border: 2px solid #ddd;padding: 5px">
        <div v-if="previousSubmission" class="float-right mt-2 mb-5 mr-5">
            <VButton variant="button bg-yellow-600 float-right" label="Edit" @click="startEditing" :disabled="editing"/>
        </div>
        <div v-if="hideUseless" class="box-content h-32 grid content-center text-red-500">
            This audio recording was marked as "Not Feedback".  
            Click "Edit" to update this information or skip to the next form.
        </div>
        <div v-else>
            <div class="mt-2 mb-5 ml-5">
                <VButton label='Mark as "Not Feedback"' variant="button_warning" :disabled="readOnly" @click="handleUseless"/>
            </div>


            <tr v-for="(question,count) in questions" :key="question.question_id">
                <td class="pad">
                    <p><span class="question">{{count+1}}. {{question.question_label}}</span>
                        <!-- <span v-if="question.required" style="color: red">*</span>    -->
                        <span v-if="question.required"> (Required)</span>   
                        <span v-else> (Optional)</span>   
                    </p>
                    <div v-if="question.type=='textarea'">
                    <textarea width="100%" rows="5" class="outline-grey" 
                    :disabled="readOnly" :name="question.name" v-model="form.responses[question.data]"/>
                    </div>
                    <div v-if="question.type=='number'">
                        <!-- <p v-if="invalidResponse(question)" class="col-span-2 md:col-span-4 text-center text-red-500">
                            <font-awesome-icon icon="exclamation-circle" class="w-6 h-6" />
                            Invalid Number: {{question.constraint}}
                        </p> -->
                        <v-input :name="question.name" type="number" mx="mx-0" :value="Number(form.responses[question.data])"
                            :disabled="readOnly" @input="updateResponse(question.data,$event.target.value)"/>
                    </div>
                    <div v-if="question.type=='select'">
                    <select :disabled="readOnly" :name="question.name" mx="mx-0" v-model="form.responses[question.data]" class="outline-grey text-black text-base">
                        <option v-for="option in question.choices" :key="option.choice_id" :value="option.value">
                            {{option.choice_label}}
                        </option>
                    </select>
                    </div>
                    <div v-else v-for="choice in question.choices" :key="choice.choice_id">
                        <input class="mr-3" @change="clearOtherAndSubChoices(choice,question)" :type="question.type" :name="question.name" 
                        :disabled="readOnly" :id="choice.choice_id" :ref="choice.choice_id" :value="choice.value" v-model="form.responses[question.data]" />
                        <label :for="choice.choice_id">{{choice.choice_label}}</label>
                        <br />
                        <div  v-if="choice.choices && String(form.responses[question.data]).includes(choice.value)">
                        <label>{{choice.question_label}}</label><span v-if="choice.required" style="color: red">*</span>   
                        <div v-for="subchoice in choice.choices" :key="subchoice.choice_id" style="text-indent: 20px">
                            <input class="mr-3" :type="choice.type" :name="choice.name" :id="choice.question_id" :value="subchoice.value" 
                            :disabled="readOnly" v-model="form.responses[choice.data]"/>
                            <label :for="subchoice.choice_id">{{subchoice.choice_label}}</label>
                        </div>
                        <div v-if="choice.data_other" style="text-indent: 20px">
                            <input :disabled="readOnly" class="mr-3" @change="clearOtherAndSubChoices(null,choice)" :type="choice.type" :name="choice.name" :id="choice.question_id+'-other'" value="other" v-model="form.responses[choice.data]"/>
                            <label :for="choice.choice_id+'-other'">Other</label>
                            <div v-if="String(form.responses[choice.data]).includes('other')">
                                <textarea :disabled="readOnly" rows="2" cols="45" class="ml-9 w-auto outline-grey" :name="choice.name+'-othertxt'" :id="choice.choice_id+'-othertxt'" v-model="form.responses[choice.data_other]"/>
                            </div>
                        </div>

                        </div>
                    </div>
                    <div v-if="question.data_other">
                        <input :disabled="readOnly" class="mr-3" @change="clearOtherAndSubChoices(null,question)" :type="question.type" 
                        :name="question.name" :id="question.question_id+'-other'" value="other" v-model="form.responses[question.data]" />
                        <label :for="question.question_id+'-other'">Other</label>
                        <span >
                            <div v-if="String(form.responses[question.data]).includes('other')">
                            <textarea :disabled="readOnly" rows="2" cols="45" class="ml-9 w-auto outline-grey" :name="question.name+'-othertxt'" :id="question.choice_id+'-othertxt'" v-model="form.responses[question.data_other]"/>
                            </div>
                        </span>
                    </div>
                </td>
            </tr>
            <tr>
            <td style="text-align: right">
                <div class="float-right">
                <v-tooltip
                    v-if="this.checkCompleted()!=''"
                    :text="checkCompleted()"
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
                    label="SUBMIT"
                    variant="success"
                    :disabled="readOnly || this.checkCompleted()!=''"
                    :iconL="submitStatus === 'submitting' ? 'spinner' : ''"
                    :iconLPulse="submitStatus === 'submitting'"
                    @click="handleUseful"
                />
                </div>
            </td>
            </tr>
        </div>
    </table>
    <div id="modalsubmit">
    <transition name="fade" appear>
        <div class="modal-overlay" v-if="showSubmitModal"></div>
    </transition>
    <transition name="pop" appear>
        <div class="modal" role="dialog" v-if="showSubmitModal"><h1>Submitted!</h1></div>
    </transition>
    </div>


  </div>
</template>

<script>
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'
import VTooltip from '@/components/VTooltip'
import VInput from '@/components/VInput'
import VButton from '@/components/VButton';

Vue.use(VueAxios,axios)


export default {
    name:"Survey",
    components: {
        VButton,
        VTooltip,
        VInput
    },
    props: ["context","uuid","submission"],
    watch: {
        submission: function(newSubmission, oldSubmission) {
            console.log("WATCH");
            this.editing = false;
            if (this.readySubmission) { 
                this.form = this.readySubmission;
            }
        }
    },
    data() {
      return {
        submitStatus: null,
        connected: true,
        showSubmitModal: false,
        editing: false,
        questions: [],
        form: {
            uuid: '',
            user_email: '',
            useless: false,
            responses: {
            // It seems anything used in v-model must be explicity declared here, instead of dynamically added in resetForm().
            resp_01:[],
            resp_02:[],
            resp_03:[],
            resp_04:[],
            resp_05:[],
            resp_06:[],
            resp_07:[],
            resp_08:[],
            resp_09:[],
            resp_10:[],
            resp_11:[],
            resp_12:[],
            resp_13:[],
            resp_14:[],
            resp_15:[],
            resp_16:[],
            resp_17:[],
            resp_18:[],
            resp_19:[],
            resp_20:[],
            resp_21:[],
            resp_22:[],
            resp_23:[],
            resp_24:[],
            resp_25:[],
            resp_26:[],
            resp_27:[],
            resp_28:[],
            resp_29:[],
            resp_30:[],
            resp_01_o:[],
            resp_02_o:[],
            resp_03_o:[],
            resp_04_o:[],
            resp_05_o:[],
            resp_06_o:[],
            resp_07_o:[],
            resp_08_o:[],
            resp_09_o:[],
            resp_10_o:[],
            resp_11_o:[],
            resp_12_o:[],
            resp_13_o:[],
            resp_14_o:[],
            resp_15_o:[],
            resp_16_o:[],
            resp_17_o:[],
            resp_18_o:[],
            resp_19_o:[],
            resp_20_o:[],
            resp_21_o:[],
            resp_22_o:[],
            resp_23_o:[],
            resp_24_o:[],
            resp_25_o:[],
            resp_26_o:[],
            resp_27_o:[],
            resp_28_o:[],
            resp_29_o:[],
            resp_30_o:[],
            }
        }
      }
    },
    methods: {
        loadQuestions() {
            const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufTQuestions?"
                + "&program=" + this.context.selectedProgramCode
                + "&deployment=" + this.context.selectedDeployment
                + "&language=" + this.context.selectedLanguageCode;
            // Vue.axios.interceptors.request.use(request => {
            //     console.log('Starting Request', JSON.stringify(request, null, 2))
            //     return request
            // });
            Vue.axios.get(request,{headers: {'Authorization': `${this.$token}`}})
            .then(response=>{
                this.questions=response.data;
                this.setDefaults();
                if (!this.connected) {
                    this.$emit('network',true);
                    this.connected = true;
                }
                //console.log(response.data);
            }).catch(err => {
                console.log("caught:"+err)
                this.$emit('network',false);
                this.connected = false;
            });
            this.resetForm();
        },
        resetForm() {
            this.form.uuid = '';
            this.form.useless = false;
            for (var i=1;i<=30;i++) {
                var field = i.toString();
                if (field.length==1) {
                field = '0'+field;
                }
                field = 'resp_' + field;
                this.form.responses[field]=[];
                this.form.responses[field+'_o']='';  // "other" field is always text
            }
            this.setDefaults();
            this.editing = false;
        },
        setDefaults() {
            for (var q of this.questions) {
                if (q.default && q.default != 'null') {
                if (q.type == 'select') {
                    this.form.responses[q.data]=q.default;
                } else {
                    this.form.responses[q.data]=[q.default];
                }
                }   
            }
        },
        updateResponse(whichResponse,whatValue) {
            this.form.responses[whichResponse] = whatValue;
            //this.getQuestionFromResponseCode(whichResponse);
        },
        // invalidResponse(question) {
        //     question.constraint = this.getPropertyFromData(whichResponse,'constraint');
        //     const data=this.form.responses[question.data]
        //     var invalid = false;
        //     if (constraint =='non-negative') {
        //         if(isNaN(data[0]) || data[0]<0) {
        //         invalid = true;
        //         }
        //     }
        //     return invalid;      
        // },
        getPropertyFromData(whichResponse,key) {
            // search the questions for data or data_other matching whichResponse
            console.log("in getProp:"+whichResponse)
            var target,question;
            // first search the top-level questions
            question = this.questions.filter((q)=>{
                return q.data==whichResponse || q.data_other==whichResponse;
            });
            if (question.length==1) {
                target = question[0]; 
            } else {
                // if not in top-level questions, it must be in a choice that has subchoices.
                question = this.questions.filter(q1=>q1.choices).map((q2)=>{
                return q2.choices.filter((c)=>{
                    return c.data==whichResponse||c.data_other==whichResponse
                })
                }).filter(q3=>q3.length>0);
                target = question[0][0];
            }
            return target[key];
        },
        clearOtherAndSubChoices(choice,question) {
            if (question.data_other && !(String(this.form.responses[question.data]).includes('other'))) {
                this.form.responses[question.data_other] = '';
            }
            if (choice && choice.data) {
                this.form.responses[choice.data]=[];
                if (choice.data_other) {
                this.form.responses[choice.data_other] = '';
                }
            }
        },
        checkCompleted() {
            let completed = "";
            let questionNumber = 0;
            for (var q of this.questions) {
                questionNumber++;
                if (q.required) {
                    if (this.form.responses[q.data]==null || this.form.responses[q.data].length == 0) {
                       completed += String(questionNumber) + ",";
                    }
                }  
                if (q.choices && q.choices.length > 0) {
                    for (var c of q.choices) {
                        //check if the subchoice would be required if its parent choice is checked 
                        if (c.required && String(this.form.responses[q.data]).includes(c.value)) {
                            //now check if this sub-choice has data
                            if (this.form.responses[c.data]==null || this.form.responses[c.data].length == 0) {
                                completed += String(questionNumber) + "." + c.value + ",";
                            }
                        }
                    }
                }
            }
            if (completed.length > 1) {
                completed = 'Questions still required:  #' + completed.substring(0, completed.length - 1);
            }
            return completed;
        },
        startEditing() {
            console.log("startEditing");
            this.editing = true;
            this.form = this.readySubmission;
        },
        handleUseless() {
            this.form.useless = true;
            this.handleSubmit();
        },
        handleUseful() {
            this.form.useless = false;
            this.handleSubmit();
        },
        handleSubmit() {
            this.submitStatus = 'submitting';
            //First, add UUID and email to the form data before we submit it.
            this.form.user_email = this.$route.query.email;
            this.form.uuid = this.uuid;

            //Submit values here:
            const action = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufProcess";      
            Vue.axios.post(action,this.form, {headers: {'Authorization': `${this.$token}`}})
            .then(response=>{
                this.connected=true;
                console.log(response.data);
                //TODO: What if Lambda function says it wasn't submitted properly
                this.showSubmitModal = true;
                this.resetForm();
                setTimeout(()=> {
                    this.showSubmitModal = false;
                },1000);
                this.getNextAudio()
            })
            .catch (err => {
                //TODO: what if network just went away before hitting submit - is data lost? can it retry?
                console.log(err);
                this.connected = false;
                this.message = 'There is no Internet connection right now.  Your survey has not been submitted yet.<BR>Please try submitting again when you have Internet.';
                setTimeout(()=> {
                    this.showSubmitModal = false;
                    this.message = '';
                },5000);
            });
            this.submitStatus = '';
        },
        getNextAudio() {

            this.$emit('next');
        }
    },
  computed: {
    readySubmission() {
        var submission = this.submission;
        if (submission) {
            var responses = submission.responses;
            for (const [key,value] of Object.entries(submission.responses)) {
                if (this.checkboxes.includes(key)) {
                    if (responses[key]) {
                        try {
                        responses[key] = responses[key].split(";");
                        } catch (e) {
                            console.log("ERR:"+(typeof responses[key]));
                        }
                    }
                    else { 
                        responses[key] = []; // null values need to be empty arrays for checkboxes to work
                    }
                }
            }
            submission.responses = responses;
        }
        return submission;
    },
    previousSubmission() {
        return (this.submission != null);
    },
    readOnly() {
          return this.previousSubmission && !this.editing;
      },
    hideUseless() {
        return (this.readOnly && this.form.useless);
    },
    // TODO: app only needs as many form.responses as the questions call for 
    //      However, v-model doesn't seem to work well if they aren't explicitly listed in vue's data() 
    // responses() {
    //  First, map this.questions to get an array of data
    //     this.questions.map(x=>x.data);
    //  Then, push to the array the other data fields:
    //      this.questions.filter(a=>a.data_other!='').map(b=>b.data_other)
    // },
    checkboxes() {
        var questionCheckboxes = this.questions.filter(a=>a.type=="checkbox").map(b=>b.data);

        var choiceCheckboxes = this.questions.reduce(
            function concatChoices(list,a){
                if(a.choices) 
                    return list.concat(a.choices); 
                else 
                    return list;
            },[])
            .filter(b=>b.type && b.type=='checkbox')
            .map(c=>c.data)
        

        return questionCheckboxes.concat(choiceCheckboxes);
    }
  },
  mounted() {
    this.loadQuestions();
  },
}
</script>


<style scoped>
table {
  margin-left: auto;
  margin-right: auto;
}
th {
  text-align: right;
  /* border-bottom: 1px solid #ddd; */
}

td {
  padding: 3px;
  text-align: left;
  /* border-bottom: 1px solid #ddd; */
}

td.stats {
  text-align: center;
}

select {
  width:100px;
}

.question {
  font-weight:bold;
  color:#58595B;
}

select:focus {
  outline:1px solid #4D90FE; 
  border:1px solid #4D90FE;
 }

:disabled {
  background-color: #D8D8D8;
}

textarea {
	width: 100%;
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
td.pad {
  padding: 15px;
  padding-top: 0px;
  vertical-align: top;
}
</style>