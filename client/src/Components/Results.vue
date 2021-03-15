<template>
  <div> 
    <div id="download-box">
      <a v-bind:href="location" download>Click here to download your weighted file</a>
      <a v-bind:href="syntax" download>Click here to download a syntax file to compute the weight</a>
    </div>
    <h3>Results</h3>
    
    <results-instructions></results-instructions> 

    <Report></Report>
    <Crosstabs></Crosstabs>
    
  </div>
</template>

<script>
import { eventBus } from '../main.js';
import ResultsInstructions from './ResultsInstructions.vue';
import Report from './Report.vue';
import Crosstabs from './Crosstabs.vue';
export default {
  data(){
    return {
      crosstabsStringArray: []
    }
  },
  props: ['location', 'syntax'],
  components:{
    ResultsInstructions,
    Report,
    Crosstabs
  },
}
</script>

<style scoped>
  #download-box {
      margin: 20px 0px;
  }

  .report-row :first-child {
    width: 190px;
    display: inline-block;
    font-weight: bold;
  }

  span + span {
    width: 100px;
    display: inline-block;
  }
</style>
