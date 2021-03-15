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
      baseUrl: 'http://127.0.0.1:5000/',
      groupSelected: '',
      report: [],
      crosstabs: []
    }
  }
});
