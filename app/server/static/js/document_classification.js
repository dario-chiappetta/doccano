import Vue from 'vue';
import annotationMixin from './mixin';
import HTTP from './http';

Vue.use(require('vue-shortkey'), {
  prevent: ['input', 'textarea'],
});


const vm = new Vue({
  el: '#mail-app',
  delimiters: ['[[', ']]'],
  mixins: [annotationMixin],

  methods: {
    isIn(label) {
      for (let i = 0; i < this.annotations[this.pageNumber].length; i++) {
        const a = this.annotations[this.pageNumber][i];
        if (a.label === label.id) {
          return a;
        }
      }
      return false;
    },

    async addLabel(label) {
      console.log("addLabel() ", label, this);
      console.log("addLabel() id2label", vm.id2label);

      const a = this.isIn(label);
      if (a) {
        this.removeLabel(a);
      } else {
        const docId = this.docs[this.pageNumber].id;
        const payload = {
          label: label.id,
        };
        await HTTP.post(`docs/${docId}/annotations/`, payload).then((response) => {
          this.annotations[this.pageNumber].push(response.data);
        });
      }
    },

    autoLabeling() {
      /*
       * TODO: race conditions still happening: a JS dev should review this code
       */

      const docId = this.docs[this.pageNumber].id;
      HTTP.get(`auto-labeling/${docId}/`).then(async (response) => {
        this.annotations[this.pageNumber].forEach(async (a) => {
          await this.removeLabel(a);
        });

        const docId = this.docs[this.pageNumber].id;
        const payload = {
          label: response.data.label,
        };
        await HTTP.post(`docs/${docId}/annotations/`, payload).then((response) => {
          console.log(response)
          // Vue.set(this.annotations, this.pageNumber, response.data);
          this.annotations[this.pageNumber].push(response.data);
        });
      });
    },
  },
});
