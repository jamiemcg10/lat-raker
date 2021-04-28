import Vue from 'vue'
import App from './App.vue'

new Vue({
  el: '#app',
  render: h => h(App)
})



export const eventBus = new Vue({
  data(){
    return {
      uid: '',
      datasetName: '',
      metaDataList: null,
      metaDataObj: null,
      dataLoaded: false,
      baseUrl: '',
      groupSelected: '',
      report: [],
      crosstabs: []
    }
  },
  created(){
    this.baseUrl = window.location.href;
  }
});
