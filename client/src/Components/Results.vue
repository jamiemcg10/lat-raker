<template>
  <div> 
    <div id="download-box">
      <a v-bind:href="location" download>Click here to download your weighted file</a>
      <a v-bind:href="syntax" download>Click here to download a syntax file to compute the weight</a>
    </div>
    <h3>Results</h3>
    <ul>
      <li>Always check to make sure the weights were computed accurately</li>
      <li>You want the weighting efficiency to be above 70, ideally above 80</li>
      <li>The minimum and maximum weight factor will show the smallest and largest weight used.</li>
    </ul>
    
    <div id="Report">
      <h4>Report</h4>
      <div class="report-row" v-for="row in reportStringArray" v-html="row"></div>
    </div>
    
    <div id="Crosstabs">
      <h4>Crosstabs</h4>
      <div v-for="row in crosstabsStringArray" v-bind:class="row.class" v-html="row.text"></div>
    </div>
  </div>
</template>

<script>
import { eventBus } from '../main.js';
export default {
  data(){
    return {
      reportStringArray: [],
      crosstabsStringArray: []
    }
  },
  methods: {
  },
  props: ['report', 'crosstabs', 'location', 'syntax'],
  created(){
    // append report and crosstabs to body
    for (let i=0; i<this.crosstabs.length; i++){
      let row = this.crosstabs[i];
      let rowString  = '';
      let rowClass = 'report-row'
      row.forEach((cell)=>{
          if (cell !== ''){
              rowString += `<span>${cell}</span>`;  // insert each cell into a span to control spacing
          }
      });
      if (row[0] === 'Question'){
          rowClass += " text";
      } else if (row[0] === 'Question Values'){
          rowString += "<span><em>%</em></span>";
      } else if (row[0] === 'Values'){
          rowClass += ' xt-labels';
      }
      this.crosstabsStringArray.push({class: rowClass, text: rowString});
    }

    for (let i=0; i<this.report.length; i++){
      let row = this.report[i];
      let rowString  = '';
      row.forEach((cell)=>{
          if (cell !== ''){
              rowString += `<span>${cell}</span>`;  // insert each cell into a span to control spacing
          }
      });

      this.reportStringArray.push(rowString);
    }
        

  }
}
</script>

<style>
</style>
