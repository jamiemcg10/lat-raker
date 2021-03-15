import Vue from 'vue'
import App from './App.vue'

new Vue({
  el: '#app',
  render: h => h(App)
})

export const eventBus = new Vue({
  data(){
    return {
      datasetName: '',
      metaDataList: null,
      metaDataObj: null,
      dataLoaded: false,
      baseUrl: 'https://latitude-rake-staging.herokuapp.com/',
      groupSelected: '',
      report: [],
      crosstabs: []
    }
  }
});
