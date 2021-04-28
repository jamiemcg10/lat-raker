<template>
    <div id="Report">
      <h4>Report</h4>
      <div class="report-row" 
        v-for="(row, i) in reportStringArray" 
        v-bind:key="i" 
        v-html="row">
      </div>
    </div>
</template>

<script>
    import { eventBus } from '../main.js';
    export default {
        data(){
            return {
                reportStringArray: []
            }
        },
        created(){
            for (let i=0; i<eventBus.report.length; i++){
            let row = eventBus.report[i];
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
  span + span {
    width: 100px;
    display: inline-block;
  }
</style>