<template>
  <div id="app">
      <h1>RIM Weight Calculator</h1>
      <p class="filename" v-if="datasetName">{{ datasetName }}</p>
      <component 
        v-bind:is="loadedComponent"
        v-on:dataLoaded="displaySelectionView($event)"
        v-on:resultsIn="displayResultsView($event)"
        v-bind:report="report"
        v-bind:crosstabs="crosstabs"
        v-bind:location="location"
        v-bind:syntax="syntax">
      </component>

  </div>
</template>

<script>
import { eventBus } from './main.js';
import FileSelector from './components/FileSelector.vue';
import SchemeDefinition from './components/SchemeDefinition.vue';
import Results from './components/Results.vue';
export default {
  data(){
    return {
      loadedComponent: 'file-selector',
      crosstabs: null,
      report: null,
      datasetName: '',
      syntax: '',
      location: '',
    }
  },
  components: {
    'file-selector': FileSelector,
    'scheme-definition': SchemeDefinition,
    'results': Results
  },
  methods: {
    displaySelectionView(data){
      this.datasetName = data;
      this.loadedComponent = 'scheme-definition';

    },
    displayResultsView(event){
      this.crosstabs = event.crosstabs;
      this.report = event.report;
      this.syntax = event.syntax;
      this.location = event.location;
      
      // fix spacing in text
      // split the report and crosstabs into arrays by new line
      // split each report and crosstabs line line into arrays by tab (3+ spaces)
      let spaceRegex = /\s{3,}/;
      this.report = this.report.split("\n");  
      this.report = this.report.map(row => row.split(spaceRegex)); 
      this.crosstabs = this.crosstabs.split("\n");  
      this.crosstabs = this.crosstabs.map(row => row.split(spaceRegex));
      
      this.loadedComponent = 'results';
      
    },
    closeResources(){
      // when user closes tab/window, tell server to delete files and session
      navigator.sendBeacon(eventBus.baseUrl+'close');
    }
  },
  created(){
    window.addEventListener('beforeunload', this.closeResources);
  }
}
</script>

<style>
  a {
      margin: 5px 0px;
      display: block;
  }

  body {
      padding: 25px;
  }

  #error {
      color: red;
      display: block;
  }

  .filename {
      font-weight: bold;
      margin-bottom: 15px;
      font-style: italic;
  }
      
  h1 {
      margin-bottom: 25px;
  }

  .inline {
      display: inline-block;
  }

  input[type="text"] {
      width: 60px;
      margin-right: 3px;
  }

  .input-group {
      margin-right: 25px;
  }

  li {
      margin: 0px 13px;
  }

  ul {
      list-style: initial;
      font-size: smaller;
      margin-bottom: 3vh;
  }

</style>
