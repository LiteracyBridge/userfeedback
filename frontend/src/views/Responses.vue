<template>
<div>
  <div v-if="allResponses" class="grid grid-cols-10">
    <div class="row-start-1 row-end-2 col-span-full" >
         <nav-bar :email="this.$route.query.email" :programs="programs" :deployments="deployments" :languages="languages" :allResponsesLink="!allResponses"  
                :selectedProgramCode="context.selectedProgramCode" :selectedDeployment="context.selectedDeployment" :selectedLanguageCode="context.selectedLanguageCode"
                @progChanged="updatedProgram" @langChanged="updatedLanguage" @deplChanged="updatedDeployment"/>
    </div>
    <div class="row-start-2 col-start-3 col-span-6 pl-8 justify-self-start text-3xl text-gray-600" style="font-weight:bold;">All Responses</div>
    <div class="row-start-3 col-start-3 col-span-6 justify-self-stretch">
      <table class="table-fixed overflow-x-auto" style="border: 2px solid #ddd">
        <thead>
          <tr>
            <th :class="col.class" v-for="col in columns" :key="col.key">
              <v-tooltip :width="150" :text="`Sort ${sortTable.descending ? 'Ascending' : 'Descending'}`">
                <button class="flex gap-2" style="white-space: nowrap;" @click="setSortByColumn(col.key)" @keyup.enter="setSortByColumn(col.key)" @keyup.space="setSortByColumn(col.key)">
                  {{ col.label }}
                  <font-awesome-icon v-if="sortTable.by === col.key" :icon="sortTable.descending ? 'chevron-down' : 'chevron-up'"/>
                </button>
              </v-tooltip>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(submission, index) in liveSubmissionsList" :key="submission.uuid"
            :class="(index % 2 === 0 ? '' : 'bg-gray-200 ') + (reviewed.includes(submission.uuid) ? 'font-normal' : 'font-semibold')" 
            class="hover:bg-gray-400 cursor-pointer" @click="goTo(submission.uuid,index)">
            <td v-for="col in columns" :key="`${index}-${col.key}`" class="text-center px-4 py-2 border-b">
              {{ submission[col.key] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div v-else-if="!allResponses">
    <analyze-comp :nextUUID="uuid" @all="setAllResponses" @next="getNext"/>
  </div>
</div>
</template>

<script>
import NavBar from "../components/NavBar.vue";
import AnalyzeComp from '../components/AnalyzeComp.vue';
import VTooltip from '@/components/VTooltip'
import axios from 'axios'
import Vue from 'vue'
import VueAxios from 'vue-axios'


Vue.use(VueAxios,axios)

const columns = [
  {
    label: 'Submission Time',
    key: 'submissionTime',
    class: 'text-center px-4 py-2 border-b'
  },{
    label: 'Filename',
    key: 'uuid',
    class: 'text-center px-4 py-2 border-b'
  },{
    label: 'Feedback',
    key: 'feedback',
    class: 'text-center px-4 py-2 border-b'
  },{
    label: 'Location',
    key: 'location',
    class: 'text-center px-4 py-2 border-b'
  },{
    label: 'Group',
    key: 'group',
    class: 'text-center px-4 py-2 border-b'
  }]


export default {
  name:"Responses",
  components: {
    NavBar,
    AnalyzeComp,
    VTooltip
  },
  data() {
    return {
      allResponses: true,
      connected: true,
      uuid:'',
      index:0,
      submissionsList: [],
      reviewed: [],
      columns,
      sortTable: {
            by: 'submissionTime',
            descending: true
      },
      submissionsToShow: 20,
      programs: [{
        code:"CARE-ETH-GIRLS",
        name:"CARE Ethiopia Girls",
        languages:[{
          code:"aar",
          name:"Afar af"
        }],
        deployments:[1]
      },{
        code:"CARE-ETH-BOYS",
        name:"CARE Ethiopia Boys",
        languages:[{
          code:"aar",
          name:"Afar af"
        }],
        deployments:[1]
      }],
      context: {
        selectedProgramCode:"CARE-ETH-GIRLS",
        selectedDeployment:1,
        selectedLanguageCode:"aar"
      }
    }
  },
  methods: {
    setAllResponses() {
        this.allResponses = true;
        this.getSubmissionsList();
    },
    goTo(uuid,index) {
        this.uuid = uuid;
        this.index = index;
        this.reviewed.push(this.submissionsList[index].uuid)
        this.allResponses = false;
    },
    getNext() {
        this.index += 1;
        if (this.index < this.submissionsList.length) {
            this.uuid = this.submissionsList[this.index].uuid;
            this.reviewed.push(this.submissionsList[this.index].uuid)
        } else {
            this.uuid = '';
        }
    },
    setSortByColumn(colId=this.sortTable.by,descending=!this.sortTable.descending) {
        console.log("sort:"+colId+" / " + String(descending));
        if (this.sortTable.by === colId) {
            this.sortTable.descending = descending
        } else {
            this.sortTable.by = colId
            this.sortTable.descending = descending;
        }
        const direction = this.sortTable.descending ? -1 : 1
        this.submissionsList = this.submissionsList.sort((a, b) =>
            direction * a[colId].toString().localeCompare(b[colId].toString())
      )

    },
    updatedProgram(programCode) {
          this.context.selectedProgramCode = programCode;
          this.context.selectedLanguageCode = this.languages[0].code;
          this.context.selectedDeployment = this.deployments[0];
          this.$router.push({ path: this.$route.path+'?email='+this.$route.query.email+'&program='+this.context.selectedProgramCode+'&language='+this.context.selectedLanguageCode+'&deployment='+this.context.selectedDeployment});
          this.getSubmissionsList();
    },
    updatedLanguage(languageCode) {
      this.context.selectedLanguageCode = languageCode;
      this.$router.push({ path: this.$route.path+'?email='+this.$route.query.email+'&program='+this.context.selectedProgramCode+'&language='+this.context.selectedLanguageCode+'&deployment='+this.context.selectedDeployment});
      this.getSubmissionsList();
    },
    updatedDeployment(deployment) {
      this.context.selectedDeployment = deployment;
      this.$router.push({ path: this.$route.path+'?email='+this.$route.query.email+'&program='+this.context.selectedProgramCode+'&language='+this.context.selectedLanguageCode+'&deployment='+this.context.selectedDeployment});
      this.getSubmissionsList();
    },
    getSubmissionsList() {    
      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufTDataService?"
          + "email=" + this.$route.query.email
          + "&program=" + this.context.selectedProgramCode
          + "&deployment=" + this.context.selectedDeployment
          + "&language=" + this.context.selectedLanguageCode
          + "&uuid=all"
          + "&timezoneOffset=" + (-new Date().getTimezoneOffset()) + ' minutes';
      // Vue.axios.interceptors.request.use(request => {console.log('Starting Request', JSON.stringify(request, null, 2)) return request });
      console.log("updateUrl:"+request);
      Vue.axios.get(request,{headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
          if (!this.connected) {
              this.connected = true;
          }
          this.submissionsList = response.data;
          this.setSortByColumn(this.sortTable.by,this.sortTable.descending);
      }).catch(err => {
          console.log("caught:"+err)
          this.connected = false;
      })
    }
  },
   computed: {
    liveSubmissionsList() {
        return this.submissionsList;
    },
    deployments() {
      var program = this.programs.filter((p)=>{
        return p.code==this.context.selectedProgramCode;
        });
      return program[0].deployments;
    },
    languages() {
      var program = this.programs.filter((p)=>{
        return p.code==this.context.selectedProgramCode;
        });
      return program[0].languages;
    }
   },
   created() {
    if(this.$route.query.program) {
        this.context.selectedProgramCode=this.$route.query.program;
        this.context.selectedLanguageCode=this.$route.query.language;
        this.context.selectedDeployment=this.$route.query.deployment;
    }
   },
   mounted() {
     this.getSubmissionsList();
   }
}
</script>
<style scoped>
table thead th {
  white-space: nowrap;
  @apply px-4 py-2 text-green border-b;
}

</style>