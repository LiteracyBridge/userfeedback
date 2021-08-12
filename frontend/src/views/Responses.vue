<template>
<div>
  <div v-if="allResponses">
    <nav-bar :programs="programs" :selectedProgramCode="context.selectedProgramCode" :email="this.$route.query.email" @changed="updatedProgram"/>
    <div v-if="submissionsList.length > 0" class="block pt-8 overflow-x-auto">
      <table class="table-fixed overflow-x-auto">
        <thead>
          <tr>
            <th :class="col.class" v-for="col in columns" :key="col.key">
              <v-tooltip :width="150" :text="`Sort ${sortTable.descending ? 'Ascending' : 'Descending'}`">
                <button
                  class="flex gap-2"
                  style="white-space: nowrap;"
                  @click="setSortByColumn(col.key)"
                  @keyup.enter="setSortByColumn(col.key)"
                  @keyup.space="setSortByColumn(col.key)"
                >
                  {{ col.label }}
                    <font-awesome-icon
                      v-if="sortTable.by === col.key"
                      :icon="sortTable.descending ? 'chevron-down' : 'chevron-up'"
                    />
                </button>
              </v-tooltip>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(submission, index) in liveSubmissionsList" :key="submission.uuid"
            :class="index % 2 === 0 ? '' : 'bg-gray-200'" class="hover:bg-gray-400" @click="goTo(submission.uuid,index)">
            <td v-for="col in columns" :key="`${index}-${col.key}`" class="text-center px-4 py-2 border-b">
              {{ submission[col.key] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
  <div v-else>
    <analyze-comp @key="uuid" :nextUUID="uuid" @all="setAllResponses" @next="getNext"/>
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
    class: 'text-center px-4 py-2 border-b w-1/4'
  },{
    label: 'Filename',
    key: 'uuid',
    class: 'text-center px-4 py-2 border-b w-1/2'
  },{
    label: 'Feedback',
    key: 'feedback',
    class: 'text-center px-4 py-2 border-b w-1/8'
  },{label: 'Reviewed',
    key: 'reviewed',
    class: 'text-center px-4 py-2 border-b w-1/8'
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
    },
    goTo(uuid,index) {
        this.uuid = uuid;
        this.index = index;
        this.submissionsList[index].reviewed = true;
        this.allResponses = false;
    },
    getNext() {
        this.index += 1;
        if (this.index < this.submissionsList.length) {
            this.uuid = this.submissionsList[this.index].uuid;
            this.submissionsList[this.index].reviewed = true;

        } else {
            this.uuid = '';
        }
    },
    setSortByColumn(colId) {
        if (this.sortTable.by === colId) {
            this.sortTable.descending = !this.sortTable.descending
        } else {
            this.sortTable.by = colId
            this.sortTable.descending = false
        }
        const direction = this.sortTable.descending ? 1 : -1
        console.log(this.submissionsList);
        this.submissionsList = this.submissionsList.sort((a, b) =>
            direction * a[colId].toString().localeCompare(b[colId].toString())
      )

    },
    updatedProgram(programCode) {
          console.log(programCode);
          this.context.selectedProgramCode = programCode;
          this.context.selectedLanguageCode = this.languages[0].code;
          this.context.selectedDeployment = this.deployments[0];
    },
    getSubmissionsList() {    
      const request = "https://ckz0f72fjf.execute-api.us-west-2.amazonaws.com/default/ufTDataService?"
          + "email=" + this.$route.query.email
          + "&program=" + this.context.selectedProgramCode
          + "&deployment=" + this.context.selectedDeployment
          + "&language=" + this.context.selectedLanguageCode
          + "&uuid=all"
          + "&timezoneOffset=" + new Date().getTimezoneOffset();
      // Vue.axios.interceptors.request.use(request => {console.log('Starting Request', JSON.stringify(request, null, 2)) return request });
      console.log("updateUrl:"+request);
      Vue.axios.get(request,{headers: {'Authorization': `${this.$token}`}})
      .then(response=>{
          if (!this.connected) {
              this.connected = true;
          }
          this.submissionsList = response.data;
          for (var s of this.submissionsList) {
              s.reviewed = false;
          }
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