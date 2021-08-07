<template>
    <span>
        Deployment 
        <select v-model="deployment" class="mt-3 mr-24 outline-grey" @change="$emit('deplChanged',deployment)">
            <option v-for="deployment in deployments" :value="deployment" :key="deployment"><span> {{deployment}}</span></option>
        </select>
        Language 
        <select v-model="languageCode" class="outline-grey" @change="$emit('langChanged',languageCode)">
            <option v-for="language in languages" :value="language.code" :key="language.code"><span> {{language.name}}</span></option>
        </select>
    </span>          
</template>

<script>
export default {
    name: "DeplLangSelect",
    props: ["deployments",
            "languages",
            "selectedDeployment",
            "selectedLanguageCode"],
    data () {
        return {
            deployment:'',
            languageCode:''
        }
    },
    mounted () {
        this.deployment = this.selectedDeployment;
        this.languageCode = this.selectedLanguageCode;
    }
}
</script>
